flectra.define('wysiwyg.widgets',function(require){
'usestrict';

varDialog=require('wysiwyg.widgets.Dialog');
varAltDialog=require('wysiwyg.widgets.AltDialog');
varMediaDialog=require('wysiwyg.widgets.MediaDialog');
varLinkDialog=require('wysiwyg.widgets.LinkDialog');
varImageCropWidget=require('wysiwyg.widgets.ImageCropWidget');
const{ColorpickerDialog}=require('web.Colorpicker');

varmedia=require('wysiwyg.widgets.media');

return{
    Dialog:Dialog,
    AltDialog:AltDialog,
    MediaDialog:MediaDialog,
    LinkDialog:LinkDialog,
    ImageCropWidget:ImageCropWidget,
    ColorpickerDialog:ColorpickerDialog,

    MediaWidget:media.MediaWidget,
    SearchableMediaWidget:media.SearchableMediaWidget,
    FileWidget:media.FileWidget,
    ImageWidget:media.ImageWidget,
    DocumentWidget:media.DocumentWidget,
    IconWidget:media.IconWidget,
    VideoWidget:media.VideoWidget,
};
});
