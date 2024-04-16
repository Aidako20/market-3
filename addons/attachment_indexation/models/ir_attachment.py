#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importio
importlogging
importxml.dom.minidom
importzipfile

fromflectraimportapi,models
fromflectra.tools.lruimportLRU

_logger=logging.getLogger(__name__)

try:
    frompdfminer.pdfinterpimportPDFResourceManager,PDFPageInterpreter
    frompdfminer.converterimportTextConverter
    frompdfminer.pdfpageimportPDFPage
exceptImportError:
    PDFResourceManager=PDFPageInterpreter=TextConverter=PDFPage=None
    _logger.warning("AttachmentindexationofPDFdocumentsisunavailablebecausethe'pdfminer'Pythonlibrarycannotbefoundonthesystem."
                    "Youmayinstallitfromhttps://pypi.org/project/pdfminer.six/(e.g.`pip3installpdfminer.six`)")

FTYPES=['docx','pptx','xlsx','opendoc','pdf']


index_content_cache=LRU(1)

deftextToString(element):
    buff=u""
    fornodeinelement.childNodes:
        ifnode.nodeType==xml.dom.Node.TEXT_NODE:
            buff+=node.nodeValue
        elifnode.nodeType==xml.dom.Node.ELEMENT_NODE:
            buff+=textToString(node)
    returnbuff


classIrAttachment(models.Model):
    _inherit='ir.attachment'

    def_index_docx(self,bin_data):
        '''IndexMicrosoft.docxdocuments'''
        buf=u""
        f=io.BytesIO(bin_data)
        ifzipfile.is_zipfile(f):
            try:
                zf=zipfile.ZipFile(f)
                content=xml.dom.minidom.parseString(zf.read("word/document.xml"))
                forvalin["w:p","w:h","text:list"]:
                    forelementincontent.getElementsByTagName(val):
                        buf+=textToString(element)+"\n"
            exceptException:
                pass
        returnbuf

    def_index_pptx(self,bin_data):
        '''IndexMicrosoft.pptxdocuments'''

        buf=u""
        f=io.BytesIO(bin_data)
        ifzipfile.is_zipfile(f):
            try:
                zf=zipfile.ZipFile(f)
                zf_filelist=[xforxinzf.namelist()ifx.startswith('ppt/slides/slide')]
                foriinrange(1,len(zf_filelist)+1):
                    content=xml.dom.minidom.parseString(zf.read('ppt/slides/slide%s.xml'%i))
                    forvalin["a:t"]:
                        forelementincontent.getElementsByTagName(val):
                            buf+=textToString(element)+"\n"
            exceptException:
                pass
        returnbuf

    def_index_xlsx(self,bin_data):
        '''IndexMicrosoft.xlsxdocuments'''

        buf=u""
        f=io.BytesIO(bin_data)
        ifzipfile.is_zipfile(f):
            try:
                zf=zipfile.ZipFile(f)
                content=xml.dom.minidom.parseString(zf.read("xl/sharedStrings.xml"))
                forvalin["t"]:
                    forelementincontent.getElementsByTagName(val):
                        buf+=textToString(element)+"\n"
            exceptException:
                pass
        returnbuf

    def_index_opendoc(self,bin_data):
        '''IndexOpenDocumentdocuments(.odt,.ods...)'''

        buf=u""
        f=io.BytesIO(bin_data)
        ifzipfile.is_zipfile(f):
            try:
                zf=zipfile.ZipFile(f)
                content=xml.dom.minidom.parseString(zf.read("content.xml"))
                forvalin["text:p","text:h","text:list"]:
                    forelementincontent.getElementsByTagName(val):
                        buf+=textToString(element)+"\n"
            exceptException:
                pass
        returnbuf

    def_index_pdf(self,bin_data):
        '''IndexPDFdocuments'''
        ifPDFResourceManagerisNone:
            return
        buf=u""
        ifbin_data.startswith(b'%PDF-'):
            f=io.BytesIO(bin_data)
            try:
                resource_manager=PDFResourceManager()
                withio.StringIO()ascontent,TextConverter(resource_manager,content)asdevice:
                    logging.getLogger("pdfminer").setLevel(logging.CRITICAL)
                    interpreter=PDFPageInterpreter(resource_manager,device)

                    forpageinPDFPage.get_pages(f):
                        interpreter.process_page(page)

                    buf=content.getvalue()
            exceptException:
                pass
        returnbuf

    @api.model
    def_index(self,bin_data,mimetype,checksum=None):
        ifchecksum:
            cached_content=index_content_cache.get(checksum)
            ifcached_content:
                returncached_content
        res=False
        forftypeinFTYPES:
            buf=getattr(self,'_index_%s'%ftype)(bin_data)
            ifbuf:
                res=buf.replace('\x00','')
                break

        res=resorsuper(IrAttachment,self)._index(bin_data,mimetype,checksum=checksum)
        ifchecksum:
            index_content_cache[checksum]=res
        returnres
