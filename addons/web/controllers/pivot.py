#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdeque
importio
importjson

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.toolsimportustr
fromflectra.tools.miscimportxlsxwriter


classTableExporter(http.Controller):

    @http.route('/web/pivot/check_xlsxwriter',type='json',auth='none')
    defcheck_xlsxwriter(self):
        returnxlsxwriterisnotNone

    @http.route('/web/pivot/export_xlsx',type='http',auth="user")
    defexport_xlsx(self,data,token):
        jdata=json.loads(data)
        output=io.BytesIO()
        workbook=xlsxwriter.Workbook(output,{'in_memory':True})
        worksheet=workbook.add_worksheet(jdata['title'])

        header_bold=workbook.add_format({'bold':True,'pattern':1,'bg_color':'#AAAAAA'})
        header_plain=workbook.add_format({'pattern':1,'bg_color':'#AAAAAA'})
        bold=workbook.add_format({'bold':True})

        measure_count=jdata['measure_count']
        origin_count=jdata['origin_count']

        #Step1:writingcolgroupheaders
        col_group_headers=jdata['col_group_headers']

        #x,y:currentcoordinates
        #carry:queuecontainingcellinformationwhenacellhasa>=2height
        #     andthedrawingcodeneedstoaddemptycellsbelow
        x,y,carry=1,0,deque()
        fori,header_rowinenumerate(col_group_headers):
            worksheet.write(i,0,'',header_plain)
            forheaderinheader_row:
                while(carryandcarry[0]['x']==x):
                    cell=carry.popleft()
                    forjinrange(measure_count*(2*origin_count-1)):
                        worksheet.write(y,x+j,'',header_plain)
                    ifcell['height']>1:
                        carry.append({'x':x,'height':cell['height']-1})
                    x=x+measure_count*(2*origin_count-1)
                forjinrange(header['width']):
                    worksheet.write(y,x+j,header['title']ifj==0else'',header_plain)
                ifheader['height']>1:
                    carry.append({'x':x,'height':header['height']-1})
                x=x+header['width']
            while(carryandcarry[0]['x']==x):
                cell=carry.popleft()
                forjinrange(measure_count*(2*origin_count-1)):
                    worksheet.write(y,x+j,'',header_plain)
                ifcell['height']>1:
                    carry.append({'x':x,'height':cell['height']-1})
                x=x+measure_count*(2*origin_count-1)
            x,y=1,y+1

        #Step2:writingmeasureheaders
        measure_headers=jdata['measure_headers']

        ifmeasure_headers:
            worksheet.write(y,0,'',header_plain)
            formeasureinmeasure_headers:
                style=header_boldifmeasure['is_bold']elseheader_plain
                worksheet.write(y,x,measure['title'],style)
                foriinrange(1,2*origin_count-1):
                    worksheet.write(y,x+i,'',header_plain)
                x=x+(2*origin_count-1)
            x,y=1,y+1
            #setminimumwidthofcellsto16whichisaround88px
            worksheet.set_column(0,len(measure_headers),16)

        #Step3:writingoriginheaders
        origin_headers=jdata['origin_headers']

        iforigin_headers:
            worksheet.write(y,0,'',header_plain)
            fororigininorigin_headers:
                style=header_boldiforigin['is_bold']elseheader_plain
                worksheet.write(y,x,origin['title'],style)
                x=x+1
            y=y+1

        #Step4:writingdata
        x=0
        forrowinjdata['rows']:
            worksheet.write(y,x,row['indent']*'    '+ustr(row['title']),header_plain)
            forcellinrow['values']:
                x=x+1
                ifcell.get('is_bold',False):
                    worksheet.write(y,x,cell['value'],bold)
                else:
                    worksheet.write(y,x,cell['value'])
            x,y=0,y+1

        workbook.close()
        xlsx_data=output.getvalue()
        response=request.make_response(xlsx_data,
            headers=[('Content-Type','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Disposition','attachment;filename=table.xlsx')],
            cookies={'fileToken':token})

        returnresponse
