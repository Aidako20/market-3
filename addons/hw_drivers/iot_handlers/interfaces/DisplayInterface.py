#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromreimportsub,finditer
importsubprocess

fromflectra.addons.hw_drivers.interfaceimportInterface


classDisplayInterface(Interface):
    _loop_delay=0
    connection_type='display'

    defget_devices(self):
        display_devices={}
        displays=subprocess.check_output(['tvservice','-l']).decode()
        x_screen=0
        formatchinfinditer('DisplayNumber(\d),typeHDMI(\d)',displays):
            display_id,hdmi_id=match.groups()
            tvservice_output=subprocess.check_output(['tvservice','-nv',display_id]).decode().strip()
            iftvservice_output:
                display_name=tvservice_output.split('=')[1]
                display_identifier=sub('[^a-zA-Z0-9]+','',display_name).replace('','_')+"_"+str(hdmi_id)
                iot_device={
                    'identifier':display_identifier,
                    'name':display_name,
                    'x_screen':str(x_screen),
                }
                display_devices[display_identifier]=iot_device
                x_screen+=1

        ifnotlen(display_devices):
            #Nodisplayconnected,create"fake"devicetobeaccessedfromanothercomputer
            display_devices['distant_display']={
                'name':"DistantDisplay",
            }

        returndisplay_devices
