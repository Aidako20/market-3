#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models

frompathlibimportPath
fromreportlab.graphics.shapes importImageasReportLabImage
fromreportlab.lib.unitsimportmm

CH_QR_CROSS_SIZE_RATIO=0.1522#RatiobetweenthesidelengthoftheSwissQR-codecrossimageandtheQR-code's
CH_QR_CROSS_FILE=Path('../static/src/img/CH-Cross_7mm.png')#ImagefilecontainingtheSwissQR-codecrosstoaddontopoftheQR-code

classIrActionsReport(models.Model):
    _inherit='ir.actions.report'

    @api.model
    defget_available_barcode_masks(self):
        rslt=super(IrActionsReport,self).get_available_barcode_masks()
        rslt['ch_cross']=self.apply_qr_code_ch_cross_mask
        returnrslt

    @api.model
    defapply_qr_code_ch_cross_mask(self,width,height,barcode_drawing):
        cross_width=CH_QR_CROSS_SIZE_RATIO*width
        cross_height=CH_QR_CROSS_SIZE_RATIO*height
        cross_path=Path(__file__).absolute().parent/CH_QR_CROSS_FILE
        qr_cross=ReportLabImage((width/2-cross_width/2)/mm,(height/2-cross_height/2)/mm,cross_width/mm,cross_height/mm,cross_path.as_posix())
        barcode_drawing.add(qr_cross)
