import json
import network
import uasyncio as asyncio
import ntptime
import screen
from machine import WDT, Pin, soft_reset
import ota
import sys
import socket
import time
import gc

# Config file
try:
    with open('/params.json', 'rb') as f:
        params = json.load(f)
except OSError:
    print('Config file not found!')
    sys.exit(0)
        
# Globals
log_list = []
start_time = 0
btn = None
width = const(122)
height = const(250)

# Logging (25 rows max)
def logging(_str, func_name='unknown', severity='INFO', _show=False):
    global log_list

    if _show:
        screen.clear()
        screen.draw_text(_str, 0, 0, 1)
        screen.update_fast()

    if len(log_list) == 25:
        log_list.pop(0)
    print('{} | {} | {} | {}'.format(time.time(), severity, func_name, _str))
    log_list.append('{} | {} | {} | {}'.format(time.time(), severity, func_name, _str))

# Button handler
def btn_event():
    if btn.value() == 0:
        utime.sleep_ms(10)
        count = 0
        # hold
        while btn.value() == 0:
            count += 1
            utime.sleep_ms(10)
            if count >= 500:
                screen.clear()
                screen.update()
                mainloop.stop()
                return
        # click
        if count > 100:
            logging("Modo desarrollo", 'btn_event()')
            mainloop.stop()
            return
        if count > 0:
            sync_time()
            show_time(force=True)

# HTML template for the webpage
async def webpage(request, writer, *_values):
    global log_list
    global start_time

    frame_dict = {}

    # PicoW uptime to text
    curr_uptime = time.time() - start_time
    _hours = curr_uptime // 3600
    _minutes = (curr_uptime % 3600) // 60
    _seconds = curr_uptime % 60
    _uptime = '{:02}:{:02}:{:02}'.format(_hours, _minutes, _seconds)
    
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(str("""<!DOCTYPE html>
            <html>
                <head>
                    <title>PicoW BLE -> MQTT</title>
                    <meta charset="UTF-8">
                </head>
                <body>
                    <div>
                        <p>PicoW BLE -> MQTT | Uptime {} | RAM usage: {}/{} ({}%)</p>
                        <p style='position: fixed; top: 0px !important; right: 1em !important;'><a href="/reset">Click to reset the PicoW</a></p>
                    </div>""".format(_uptime, gc.mem_alloc(), gc.mem_alloc()+gc.mem_free(), round(100 * float(gc.mem_alloc())/float(gc.mem_alloc()+gc.mem_free()), 2))))
    await writer.drain()


    if request == '/pending':
        writer.write(str("""
                    <div>
                        <p><a href="/">Back</a></p>
                        <h1>List of devices pending to send ({})</h1>
                        <table>
                            <thead>
                                <tr>
                                    <th>addr</th>
                                    <th>rssi</th>
                                    <th>raw_data</th>
                                    <th>data</th>
                                    <th>timestamp</th>
                                </tr>
                            </thead>
                            <tbody>""".format()))

        for curr_addr, curr_frame in frame_dict.items():
            if curr_frame:
                curr_data = {}
                if 'data' in curr_frame.keys():
                    curr_data = curr_frame['data']

                writer.write(str("""   
                                <tr>
                                    <td>{}</td>
                                    <td>{}</td>
                                    <td>{}</td>
                                    <td>{}</td>
                                    <td>{}</td>
                                <tr>""".format(curr_addr, curr_frame['rssi'], curr_frame['raw_data'], json.dumps(curr_data), curr_frame['timestamp'])))
                await writer.drain()

        writer.write(str("""</tbody>
                        </table>
                    </div>"""))

    elif request == '/log':
        writer.write(str("""
                    <div>
                        <p><a href="/">Back</a></p>
                        <h1>Logs:</h1>"""))

        for curr_log in log_list:
            writer.write(str("""<p>{}</p>""".format(curr_log)))
            await writer.drain()

        writer.write(str("""</div>"""))

    elif request == '/reset':
        writer.write(str("""
                    <div>
                        <h1>Do you want to reboot the PicoW?</h1>
                        <p><a href="/reset_confirm">YES</a>&emsp;<a href="/">NO</a></p>
                    </div>"""))

    # Default page
    else:
        pending_total = 0
        for curr_addr, curr_frame in frame_dict.items():
            if curr_frame:
                pending_total += 1

        writer.write(str("""
                    <div>
                        <p>Total devices pendind to send PicoW: {} <a href="/pending">Pending list ({})</a></p>
                        <p>{} lines saved in log <a href="/log">See logs</a></p>
                    </div>""".format(len(list(frame_dict.keys())), pending_total, len(log_list))))

    writer.write(str("""
                </body>
            </html>"""))
    await writer.drain()
    
# Asynchronous function to handle client's requests
async def handle_client(reader, writer):
    #logging("Client connected", 'handle_client()', 'DEBUG')
    request_line = await reader.readline()
    
    # Skip HTTP request headers
    while await reader.readline() != b"\r\n":
        pass
    
    request = str(request_line, 'utf-8').split()[1]
    #logging('Request: {}'.format(request), 'handle_client()', 'DEBUG')
    
    # Process the special requests
    if request == '/reset_confirm':
        soft_reset()

    # Generate HTML response and send the response
    await webpage(request, writer)  

    # Close the connection
    await writer.drain()
    await writer.wait_closed()
    gc.collect()
    #logging("Client disconnected", 'handle_client()', 'DEBUG')

# Respond to connectivity being (re)established
async def up():
    while True:
        await asyncio.sleep(0.5)
        #await client.up.wait()  # Wait on an Event
        #client.up.clear()

# Network starting and OTA update
async def init():
    global params
    global btn
    
    # Import commong icons
    from icons_32.spinner import __get_icon as spinner_32
    from icons_32.check import __get_icon as check_32
    from icons_32.cross import __get_icon as cross_32
    
    # init btn
    btn = Pin(39, Pin.IN)
    
    # Connect to WiFi
    logging("Connecting to WiFi", 'init()')
    screen.draw_text('Wifi:',10,10,2)
    screen.draw_fb(spinner_32(), 100, 10, 1)
    screen.update_fast()
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    not_found = True
    for winfo in sta_if.scan():
        name = winfo[0].decode()
        if name == params['ssid']:
            not_found = False
            sta_if.connect(name, params['wifi_pw'])
            break
    count = 0
    while not sta_if.isconnected() and count < 30 and not not_found:
        count += 1
        await asyncio.sleep(1)
    if count >= 30 or not_found:
        logging("Failed to init WiFi", 'init()')
        from icons_32.no_wifi import __get_icon as no_wifi_32
        screen.draw_fb(no_wifi_32(), 100, 10, 1)
        screen.update_fast()
        del no_wifi_32
        await asyncio.sleep(1)
        return
    
    curr_ip = sta_if.ifconfig()[0]
    logging("IP: {}".format(curr_ip), 'init()')
    from icons_32.wifi import __get_icon as wifi_32
    screen.draw_fb(wifi_32(), 100, 10, 1)
    screen.draw_text('IP:', 200, 10, 1)
    screen.draw_text(curr_ip, 130, 30, 1)
    screen.update_fast()
    del wifi_32
    gc.collect()
    
    # Updating system clock
    logging("Updating system time", 'init()')
    screen.draw_text('NTP:',10,50,2)
    screen.draw_fb(spinner_32(), 80, 50, 1)
    screen.update_fast()
    ntptime.host = params['ntp_host']
    ntptime.timeout = 10
    try:
        ntptime.settime()
        screen.draw_fb(check_32(), 80, 50, 1)
        screen.update_fast()
    except:
        screen.draw_fb(check_32(), 80, 50, 1)
        screen.update_fast()
        return
    
    # Checking for OTA Update
    logging("Checking for OTA Update", 'init()')
    screen.draw_text('OTA:',10,90,2)
    screen.draw_fb(spinner_32(), 80, 90, 1)
    screen.update_fast()
    firmware_url = "https://github.com/{}/{}/{}/".format(params['GitHub_username'], params['repo_name'], params['branch'])
    ota_updater = ota.OTAUpdater(logging, firmware_url, 'main.py')
    from icons_32.download import __get_icon as download_32
    screen.draw_fb(download_32(), 80, 90, 1)
    screen.update_fast()
    ota_updater.download_and_install_update_if_available()
    screen.draw_fb(check_32(), 80, 90, 1)
    screen.update_fast()
    del ota_updater
    del download_32
    
    del spinner_32
    del check_32
    del cross_32
    gc.collect()

# ??? client and local Webserver
async def main():

    # Connect to ???
    #logging("Connecting to ???", 'main()')
    #await client.connect()
    #logging("Connected", 'main()')
    #asyncio.create_task(up())
    
    # Start the webserver on port 80
    logging('Setting up server', 'main()')
    server = asyncio.start_server(handle_client, "0.0.0.0", 80)
    asyncio.create_task(server)

    global start_time
    start_time = time.time()
    logging('All up and running!', 'main()')

    # Watchdog timer
    wdt = WDT(timeout=8388)

    while True:
        try:
            pass

        except Exception as e:
            logging(e, 'main()', 'ERROR')
        
        wdt.feed()
        await asyncio.sleep(0.5)

# MAIN #
if __name__ == "__main__":
    try:
        # Init screen
        screen.init()
        screen.clear()
        screen.update()

        # Run init (WiFi/OTA/NTP)
        asyncio.run(init())
        
        # Removing OTA module from RAM
        del ota
        del sys.modules["ota"]
        gc.collect()
        
        # Run main loop
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        loop.run_forever()
    except Exception as e:
        print(e)
        soft_reset() 
    finally:
        sys.exit(0)