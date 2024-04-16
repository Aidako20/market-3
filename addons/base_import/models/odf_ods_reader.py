#Copyright2011MarcoConti

#LicensedundertheApacheLicense,Version2.0(the"License");
#youmaynotusethisfileexceptincompliancewiththeLicense.
#YoumayobtainacopyoftheLicenseat
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unlessrequiredbyapplicablelaworagreedtoinwriting,software
#distributedundertheLicenseisdistributedonan"ASIS"BASIS,
#WITHOUTWARRANTIESORCONDITIONSOFANYKIND,eitherexpressorimplied.
#SeetheLicenseforthespecificlanguagegoverningpermissionsand
#limitationsundertheLicense.

#sourcedfromhttps://github.com/marcoconti83/read-ods-with-odfpy
#furtheralteredlocally

fromodfimportopendocument
fromodf.tableimportTable,TableRow,TableCell
fromodf.textimportP


classODSReader(object):

    #loadsthefile
    def__init__(self,file=None,content=None,clonespannedcolumns=None):
        ifnotcontent:
            self.clonespannedcolumns=clonespannedcolumns
            self.doc=opendocument.load(file)
        else:
            self.clonespannedcolumns=clonespannedcolumns
            self.doc=content
        self.SHEETS={}
        forsheetinself.doc.spreadsheet.getElementsByType(Table):
            self.readSheet(sheet)

    #readsasheetinthesheetdictionary,storingeachsheetasan
    #array(rows)ofarrays(columns)
    defreadSheet(self,sheet):
        name=sheet.getAttribute("name")
        rows=sheet.getElementsByType(TableRow)
        arrRows=[]

        #foreachrow
        forrowinrows:
            arrCells=[]
            cells=row.getElementsByType(TableCell)

            #foreachcell
            forcount,cellinenumerate(cells,start=1):
                #repeatedvalue?
                repeat=0
                ifcount!=len(cells):
                    repeat=cell.getAttribute("numbercolumnsrepeated")
                ifnotrepeat:
                    repeat=1
                    spanned=int(cell.getAttribute('numbercolumnsspanned')or0)
                    #clonespannedcells
                    ifself.clonespannedcolumnsisnotNoneandspanned>1:
                        repeat=spanned

                ps=cell.getElementsByType(P)
                textContent=u""

                #foreachtext/text:spannode
                forpinps:
                    forninp.childNodes:
                        ifn.nodeType==1andn.tagName=="text:span":
                            forcinn.childNodes:
                                ifc.nodeType==3:
                                    textContent=u'{}{}'.format(textContent,n.data)

                        ifn.nodeType==3:
                            textContent=u'{}{}'.format(textContent,n.data)

                iftextContent:
                    ifnottextContent.startswith("#"): #ignorecommentscells
                        forrrinrange(int(repeat)): #repeated?
                            arrCells.append(textContent)
                else:
                    forrrinrange(int(repeat)):
                        arrCells.append("")

            #ifrowcontainedsomething
            ifarrCells:
                arrRows.append(arrCells)

            #else:
            #   print("Emptyorcommentedrow(",row_comment,")")

        self.SHEETS[name]=arrRows

    #returnsasheetasanarray(rows)ofarrays(columns)
    defgetSheet(self,name):
        returnself.SHEETS[name]

    defgetFirstSheet(self):
        returnnext(iter(self.SHEETS.values()))
