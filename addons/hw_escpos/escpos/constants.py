#-*-coding:utf-8-*-

"""ESC/POSCommands(Constants)"""

#Controlcharacters
ESC='\x1b'

#Feedcontrolsequences
CTL_LF   ='\x0a'            #Printandlinefeed
CTL_FF   ='\x0c'            #Formfeed
CTL_CR   ='\x0d'            #Carriagereturn
CTL_HT   ='\x09'            #Horizontaltab
CTL_VT   ='\x0b'            #Verticaltab

#RTStatuscommands
DLE_EOT_PRINTER  ='\x10\x04\x01' #Transmitprinterstatus
DLE_EOT_OFFLINE  ='\x10\x04\x02'
DLE_EOT_ERROR    ='\x10\x04\x03'
DLE_EOT_PAPER    ='\x10\x04\x04'

#Printerhardware
HW_INIT  ='\x1b\x40'        #Cleardatainbufferandresetmodes
HW_SELECT='\x1b\x3d\x01'    #Printerselect
HW_RESET ='\x1b\x3f\x0a\x00'#Resetprinterhardware
#CashDrawer(ESCp<pin><ontime:2*ms><offtime:2*ms>)
_CASH_DRAWER=lambdam,t1='',t2='':ESC+'p'+m+chr(t1)+chr(t2)
CD_KICK_2=_CASH_DRAWER('\x00',50,50) #Sendsapulsetopin2[]
CD_KICK_5=_CASH_DRAWER('\x01',50,50) #Sendsapulsetopin5[]
#Paper
PAPER_FULL_CUT ='\x1d\x56\x00'#Fullcutpaper
PAPER_PART_CUT ='\x1d\x56\x01'#Partialcutpaper
#Textformat  
TXT_NORMAL     ='\x1b\x21\x00'#Normaltext
TXT_2HEIGHT    ='\x1b\x21\x10'#Doubleheighttext
TXT_2WIDTH     ='\x1b\x21\x20'#Doublewidthtext
TXT_DOUBLE     ='\x1b\x21\x30'#Doubleheight&Width
TXT_UNDERL_OFF ='\x1b\x2d\x00'#UnderlinefontOFF
TXT_UNDERL_ON  ='\x1b\x2d\x01'#Underlinefont1-dotON
TXT_UNDERL2_ON ='\x1b\x2d\x02'#Underlinefont2-dotON
TXT_BOLD_OFF   ='\x1b\x45\x00'#BoldfontOFF
TXT_BOLD_ON    ='\x1b\x45\x01'#BoldfontON
TXT_FONT_A     ='\x1b\x4d\x00'#FonttypeA
TXT_FONT_B     ='\x1b\x4d\x01'#FonttypeB
TXT_ALIGN_LT   ='\x1b\x61\x00'#Leftjustification
TXT_ALIGN_CT   ='\x1b\x61\x01'#Centering
TXT_ALIGN_RT   ='\x1b\x61\x02'#Rightjustification
TXT_COLOR_BLACK='\x1b\x72\x00'#DefaultColor
TXT_COLOR_RED  ='\x1b\x72\x01'#AlternativeColor(UsuallyRed)

#TextEncoding

TXT_ENC_PC437  ='\x1b\x74\x00'#PC437USA
TXT_ENC_KATAKANA='\x1b\x74\x01'#KATAKANA(JAPAN)
TXT_ENC_PC850  ='\x1b\x74\x02'#PC850Multilingual
TXT_ENC_PC860  ='\x1b\x74\x03'#PC860Portuguese
TXT_ENC_PC863  ='\x1b\x74\x04'#PC863Canadian-French
TXT_ENC_PC865  ='\x1b\x74\x05'#PC865Nordic
TXT_ENC_KANJI6 ='\x1b\x74\x06'#One-passKanji,Hiragana
TXT_ENC_KANJI7 ='\x1b\x74\x07'#One-passKanji
TXT_ENC_KANJI8 ='\x1b\x74\x08'#One-passKanji
TXT_ENC_PC851  ='\x1b\x74\x0b'#PC851Greek
TXT_ENC_PC853  ='\x1b\x74\x0c'#PC853Turkish
TXT_ENC_PC857  ='\x1b\x74\x0d'#PC857Turkish
TXT_ENC_PC737  ='\x1b\x74\x0e'#PC737Greek
TXT_ENC_8859_7 ='\x1b\x74\x0f'#ISO8859-7Greek
TXT_ENC_WPC1252='\x1b\x74\x10'#WPC1252
TXT_ENC_PC866  ='\x1b\x74\x11'#PC866Cyrillic#2
TXT_ENC_PC852  ='\x1b\x74\x12'#PC852Latin2
TXT_ENC_PC858  ='\x1b\x74\x13'#PC858Euro
TXT_ENC_KU42   ='\x1b\x74\x14'#KU42Thai
TXT_ENC_TIS11  ='\x1b\x74\x15'#TIS11Thai
TXT_ENC_TIS18  ='\x1b\x74\x1a'#TIS18Thai
TXT_ENC_TCVN3  ='\x1b\x74\x1e'#TCVN3Vietnamese
TXT_ENC_TCVN3B ='\x1b\x74\x1f'#TCVN3Vietnamese
TXT_ENC_PC720  ='\x1b\x74\x20'#PC720Arabic
TXT_ENC_WPC775 ='\x1b\x74\x21'#WPC775BalticRim
TXT_ENC_PC855  ='\x1b\x74\x22'#PC855Cyrillic
TXT_ENC_PC861  ='\x1b\x74\x23'#PC861Icelandic
TXT_ENC_PC862  ='\x1b\x74\x24'#PC862Hebrew
TXT_ENC_PC864  ='\x1b\x74\x25'#PC864Arabic
TXT_ENC_PC869  ='\x1b\x74\x26'#PC869Greek
TXT_ENC_PC936  ='\x1C\x21\x00'#PC936GBK(GuobiaoKuozhan)
TXT_ENC_8859_2 ='\x1b\x74\x27'#ISO8859-2Latin2
TXT_ENC_8859_9 ='\x1b\x74\x28'#ISO8859-2Latin9
TXT_ENC_PC1098 ='\x1b\x74\x29'#PC1098Farsi
TXT_ENC_PC1118 ='\x1b\x74\x2a'#PC1118Lithuanian
TXT_ENC_PC1119 ='\x1b\x74\x2b'#PC1119Lithuanian
TXT_ENC_PC1125 ='\x1b\x74\x2c'#PC1125Ukrainian
TXT_ENC_WPC1250='\x1b\x74\x2d'#WPC1250Latin2
TXT_ENC_WPC1251='\x1b\x74\x2e'#WPC1251Cyrillic
TXT_ENC_WPC1253='\x1b\x74\x2f'#WPC1253Greek
TXT_ENC_WPC1254='\x1b\x74\x30'#WPC1254Turkish
TXT_ENC_WPC1255='\x1b\x74\x31'#WPC1255Hebrew
TXT_ENC_WPC1256='\x1b\x74\x32'#WPC1256Arabic
TXT_ENC_WPC1257='\x1b\x74\x33'#WPC1257BalticRim
TXT_ENC_WPC1258='\x1b\x74\x34'#WPC1258Vietnamese
TXT_ENC_KZ1048 ='\x1b\x74\x35'#KZ-1048Kazakhstan

TXT_ENC_KATAKANA_MAP={
  #MapsUTF-8KatakanasymbolstoKATAKANAPageCodes

  #Half-WidthKatakanas
  '\xef\xbd\xa1':'\xa1', #｡
  '\xef\xbd\xa2':'\xa2', #｢
  '\xef\xbd\xa3':'\xa3', #｣
  '\xef\xbd\xa4':'\xa4', #､
  '\xef\xbd\xa5':'\xa5', #･

  '\xef\xbd\xa6':'\xa6', #ｦ
  '\xef\xbd\xa7':'\xa7', #ｧ
  '\xef\xbd\xa8':'\xa8', #ｨ
  '\xef\xbd\xa9':'\xa9', #ｩ
  '\xef\xbd\xaa':'\xaa', #ｪ
  '\xef\xbd\xab':'\xab', #ｫ
  '\xef\xbd\xac':'\xac', #ｬ
  '\xef\xbd\xad':'\xad', #ｭ
  '\xef\xbd\xae':'\xae', #ｮ
  '\xef\xbd\xaf':'\xaf', #ｯ
  '\xef\xbd\xb0':'\xb0', #ｰ
  '\xef\xbd\xb1':'\xb1', #ｱ
  '\xef\xbd\xb2':'\xb2', #ｲ
  '\xef\xbd\xb3':'\xb3', #ｳ
  '\xef\xbd\xb4':'\xb4', #ｴ
  '\xef\xbd\xb5':'\xb5', #ｵ
  '\xef\xbd\xb6':'\xb6', #ｶ
  '\xef\xbd\xb7':'\xb7', #ｷ
  '\xef\xbd\xb8':'\xb8', #ｸ
  '\xef\xbd\xb9':'\xb9', #ｹ
  '\xef\xbd\xba':'\xba', #ｺ
  '\xef\xbd\xbb':'\xbb', #ｻ
  '\xef\xbd\xbc':'\xbc', #ｼ
  '\xef\xbd\xbd':'\xbd', #ｽ
  '\xef\xbd\xbe':'\xbe', #ｾ
  '\xef\xbd\xbf':'\xbf', #ｿ
  '\xef\xbe\x80':'\xc0', #ﾀ
  '\xef\xbe\x81':'\xc1', #ﾁ
  '\xef\xbe\x82':'\xc2', #ﾂ
  '\xef\xbe\x83':'\xc3', #ﾃ
  '\xef\xbe\x84':'\xc4', #ﾄ
  '\xef\xbe\x85':'\xc5', #ﾅ
  '\xef\xbe\x86':'\xc6', #ﾆ
  '\xef\xbe\x87':'\xc7', #ﾇ
  '\xef\xbe\x88':'\xc8', #ﾈ
  '\xef\xbe\x89':'\xc9', #ﾉ
  '\xef\xbe\x8a':'\xca', #ﾊ
  '\xef\xbe\x8b':'\xcb', #ﾋ
  '\xef\xbe\x8c':'\xcc', #ﾌ
  '\xef\xbe\x8d':'\xcd', #ﾍ
  '\xef\xbe\x8e':'\xce', #ﾎ
  '\xef\xbe\x8f':'\xcf', #ﾏ
  '\xef\xbe\x90':'\xd0', #ﾐ
  '\xef\xbe\x91':'\xd1', #ﾑ
  '\xef\xbe\x92':'\xd2', #ﾒ
  '\xef\xbe\x93':'\xd3', #ﾓ
  '\xef\xbe\x94':'\xd4', #ﾔ
  '\xef\xbe\x95':'\xd5', #ﾕ
  '\xef\xbe\x96':'\xd6', #ﾖ
  '\xef\xbe\x97':'\xd7', #ﾗ
  '\xef\xbe\x98':'\xd8', #ﾘ
  '\xef\xbe\x99':'\xd9', #ﾙ
  '\xef\xbe\x9a':'\xda', #ﾚ
  '\xef\xbe\x9b':'\xdb', #ﾛ
  '\xef\xbe\x9c':'\xdc', #ﾜ
  '\xef\xbe\x9d':'\xdd', #ﾝ

  '\xef\xbe\x9e':'\xde', #ﾞ
  '\xef\xbe\x9f':'\xdf', #ﾟ
}

#Barcodformat
BARCODE_TXT_OFF='\x1d\x48\x00'#HRIbarcodecharsOFF
BARCODE_TXT_ABV='\x1d\x48\x01'#HRIbarcodecharsabove
BARCODE_TXT_BLW='\x1d\x48\x02'#HRIbarcodecharsbelow
BARCODE_TXT_BTH='\x1d\x48\x03'#HRIbarcodecharsbothaboveandbelow
BARCODE_FONT_A ='\x1d\x66\x00'#FonttypeAforHRIbarcodechars
BARCODE_FONT_B ='\x1d\x66\x01'#FonttypeBforHRIbarcodechars
BARCODE_HEIGHT ='\x1d\x68\x64'#BarcodeHeight[1-255]
BARCODE_WIDTH  ='\x1d\x77\x03'#BarcodeWidth [2-6]
BARCODE_UPC_A  ='\x1d\x6b\x00'#BarcodetypeUPC-A
BARCODE_UPC_E  ='\x1d\x6b\x01'#BarcodetypeUPC-E
BARCODE_EAN13  ='\x1d\x6b\x02'#BarcodetypeEAN13
BARCODE_EAN8   ='\x1d\x6b\x03'#BarcodetypeEAN8
BARCODE_CODE39 ='\x1d\x6b\x04'#BarcodetypeCODE39
BARCODE_ITF    ='\x1d\x6b\x05'#BarcodetypeITF
BARCODE_NW7    ='\x1d\x6b\x06'#BarcodetypeNW7
#Imageformat 
S_RASTER_N     ='\x1d\x76\x30\x00'#Setrasterimagenormalsize
S_RASTER_2W    ='\x1d\x76\x30\x01'#Setrasterimagedoublewidth
S_RASTER_2H    ='\x1d\x76\x30\x02'#Setrasterimagedoubleheight
S_RASTER_Q     ='\x1d\x76\x30\x03'#Setrasterimagequadruple
