""" Written by Benjamin Jack Cullen """

import os.path
import datetime
import upnpclient
import socket
import codecs

enum = []
from_file_bool = False


def enumeration():
    global enum
    global from_file_bool

    from_file_bool = False

    enum = []

    print('')
    print('-' * 180)
    print('')

    print('-- attempting enumeration')

    # M-Search message body
    MS = \
        'M-SEARCH * HTTP/1.1\r\n' \
        'HOST:239.255.255.250:1900\r\n' \
        'ST:upnp:rootdevice\r\n' \
        'MX:2\r\n' \
        'MAN:"ssdp:discover"\r\n' \
        '\r\n'

    # Set up a UDP socket for multicast
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    soc.settimeout(2)

    # Send M-Search message to multicast address for UPNP
    soc.sendto(MS.encode('utf-8'), ('239.255.255.250', 1900))

    # Listen and capture returned responses
    try:
        while True:
            data, addr = soc.recvfrom(8192)
            print(addr, data)
            if data:
                enum.append([addr, data])
    except socket.timeout:
        soc.close()
        print('-- timed out')
        pass
    soc.close()

    # Create a filename using datetime
    time_str = str(datetime.datetime.now()).replace(':', '_').replace(' ', '_').replace('.', '_')
    fname = './enumeration_upnp_' + time_str + '.txt'

    # Check if file already exists
    if not os.path.exists(fname):
        codecs.open(fname, 'w', encoding='utf-8').close()

    # Write the enumerated data to file
    if os.path.exists(fname):
        with codecs.open(fname, 'w', encoding='utf-8') as fo:
            for _ in enum:
                fo.write(str(_) + '\n')
        fo.close()

    print('')
    print('-' * 180)
    print('')


def get_data():
    global enum
    global from_file_bool

    url = ''

    for _ in enum:

        print('')
        print('-' * 180)
        print('')

        if from_file_bool is False:
            # Set string
            str_ = str(_[1])

            # Find url and slice twice
            find_0 = str_.find('http')
            str_ = str_[find_0:]
            find_1 = str_.find('.xml')
            url = str_[:find_1+4]

            # Find Address
            addr = str(_[0][0] + ':' + str(_[0][1]))
            print('Attempting to retrieve information from: ', addr, ' at address url ', url)

        else:
            str_ = _

            # Find url and slice twice
            find_0 = str_.find('http')
            str_ = str_[find_0:]
            find_1 = str_.find('.xml')
            url = str_[:find_1 + 4]
            print('Attempting to retrieve information from url:', url)

        # Set device using url
        d = upnpclient.Device(url)

        # Basic information
        print('')
        print('Name:              ', d.device_name)
        print('Authentication:    ', d.http_auth)
        print('HTTP Headers:      ', d.http_headers)
        print('Device Type:       ', d.device_type)
        print('Friendly Name:     ', d.friendly_name)
        print('Location:          ', d.location)
        print('Manufacturer:      ', d.manufacturer)
        print('Manufacturer URL:  ', d.manufacturer_url)
        print('Model Name:        ', d.model_name)
        print('Model Description: ', d.model_description)
        print('Model Number:      ', d.model_number)
        print('Serial Number:     ', d.serial_number)
        print('Service Map:       ', d.service_map)
        print('UDN:               ', d.udn)

        for k in d.service_map:
            print('\n[Service]', k)

            # Magic formula
            for _ in d[k].actions:
                action = str(_).split(' ')[1].replace("'>", "").replace("'", "")
                print('         [Action]', action)
                args = d[k][action].argsdef_in
                if len(args) > 0:
                    for _ in args:
                        print('                 [Action Arguments]', _)
                else:
                    try:
                        print('                 [Action Returned]', d[k][action]())
                    except:
                        pass

    print('')
    print('-' * 180)
    print('')


def use_existing_enum_data():
    global enum
    global from_file_bool

    from_file_bool = True

    enum = []

    print('')
    print('-' * 180)
    print('')
    print('[FILE LIST]')
    fname_all = os.listdir('./')
    for _ in fname_all:
        if _.endswith('.txt') and _.startswith('enumeration_upnp_'):
            pass
        else:
            fname_all.remove(_)
    i = 0
    for _ in fname_all:
        if _.endswith('.txt') and _.startswith('enumeration_upnp_'):
            print('    ' + str(i) + ' ' + _)
            i += 1
    print('')
    user_input_1 = input('select: ')
    print('')
    print('-' * 180)
    print('')
    if user_input_1.isdigit():
        if int(user_input_1) <= len(fname_all)-1:
            fname = './' + str(fname_all[int(user_input_1)])
            print('[READING FILE] ' + str(fname))
            with codecs.open(fname, 'r', encoding='utf-8') as fo:
                for line in fo:
                    line = line.strip()
                    enum.append(line)
            for _ in enum:
                print('')
                print('[CREATED LIST ENTRY] ', _)


while True:
    print('')
    print('-' * 180)
    print('')
    print('[ UPNPOWER ]')
    print('')
    print('[ ENUMERATED DEVICES ]', len(enum))
    print('')
    print('1 [ ENUMERATE ]')
    print('2 [ SELECT PRE-ENUMERATED DATA ]')
    print('3 [ SCAN ]')
    print('')
    user_input_0 = input('select: ')

    if user_input_0 == '1':
        enumeration()

    elif user_input_0 == '2':
        use_existing_enum_data()

    elif user_input_0 == '3':
        if len(enum) > 0:
            get_data()
        else:
            print('')
            print('-- [INVALID] Zero enumerated devices selected')
