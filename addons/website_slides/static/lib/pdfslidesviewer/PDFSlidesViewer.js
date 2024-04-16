/**
    HomemadehelperforbrowsingPDFdocumentfrompagetopage.
    Thisishightlyinspiredfromhttps://github.com/mozilla/pdf.js/blob/master/examples/learning/prevnext.html
    ThislibrequiresPDFJS.ItsimplyusesPDFjsanditspromises.
    DOC:http://mozilla.github.io/pdf.js/api/draft/api.js.html
*/

//!!!!!!!!!usewindow.pdfjsLibandnotpdfjsLib

varPDFSlidesViewer=(function(){
    functionPDFSlidesViewer(pdf_url,$canvas,disableWorker){
        //pdfvariables
        this.pdf=null;
        this.pdf_url=pdf_url||false;
        this.pdf_page_total=0;
        this.pdf_page_current=1;//defaultisthefirstpage
        this.pdf_zoom=1;//1=scaletofittoavailablespace
        //promisebusiness
        this.pageRendering=false;
        this.pageNumPending=null;
        //canvas
        this.canvas=$canvas;
        this.canvas_context=$canvas.getContext('2d');
        //PDFJSbusiness
        /**
         *Disablethewebworkerandrunallcodeonthemainthread.Thiswillhappen
         *automaticallyifthebrowserdoesn'tsupportworkersorsendingtypedarrays
         *toworkers.
         *@var{boolean}
         *
         *disableWorkershouldbe'true'ifthedocumentcamefromanotheroriginthanthe
         *page(typicallythe'embedcase').
         *@seehttp://en.wikipedia.org/wiki/Cross-origin_resource_sharing.
         *thisisequivalenttotheuse_corsoptioninopenerpframework.js
         */
    };

    /**
     *LoadthePDFdocument
     *@param(optional)url:theurlofthedocumenttoload
     */
    PDFSlidesViewer.prototype.loadDocument=function(url){
        varself=this;
        varpdf_url=url||this.pdf_url;
        returnwindow.pdfjsLib.getDocument(pdf_url).then(function(file_content){
            self.pdf=file_content;
            self.pdf_page_total=file_content.numPages;
            returnfile_content;
        });
    };

    /**
     *Getpageinfofromdocument,resizecanvasaccordingly,andrenderpage.
     *@parampage_number:Pagenumber.
     */
    PDFSlidesViewer.prototype.renderPage=function(page_number){
        varself=this;
        this.pageRendering=true;
        returnthis.pdf.getPage(page_number).then(function(page){
            //EachPDFpagehasitsownviewportwhichdefinesthesizeinpixelsandinitialrotation.
            //Weprovidethescaleatwhichtorenderit(relativetothenaturalsizeofthedocument)
            varscale=self.getScaleToFit(page)*self.pdf_zoom;
            varviewport=page.getViewport({scale:scale});
            //importanttomatch,otherwisethebrowserwillscaletherenderedoutputanditwillbeugly
            self.canvas.height=viewport.height;
            self.canvas.width=viewport.width;
            //RenderPDFpageintocanvascontext
            varrenderContext={
                canvasContext:self.canvas_context,
                viewport:viewport
            };
            varrenderTask=page.render(renderContext);
            //Waitforrenderingtofinish
            returnrenderTask.promise.then(function(){
                self.pageRendering=false;
                if(self.pdf_zoom===1&&scale>self.getScaleToFit(page)){
                    //ifthescalehaschanged(becausewejustaddedscrollbars)andwenolongerfitthespace
                    returnself.renderPage(page_number);
                }
                if(self.pageNumPending!==null){
                    //Newpagerenderingispending
                    self.renderPage(self.pageNumPending);
                    self.pageNumPending=null;
                }
                self.pdf_page_current=page_number;
                returnpage_number;
            });
        });
    };

    /**
     *Ifanotherpagerenderinginprogress,waitsuntiltherenderingis
     *finised.Otherwise,executesrenderingimmediately.
     */
    PDFSlidesViewer.prototype.queueRenderPage=function(num){
        if(this.pageRendering){
            this.pageNumPending=num;//thequeueisonlythelastelem
            returnPromise.resolve(num);
        }else{
            returnthis.renderPage(num);
        }
    }

    /**
     *Displayspreviouspage.
     */
    PDFSlidesViewer.prototype.previousPage=function(){
        if(this.pdf_page_current<=1){
          returnPromise.resolve(false);
        }
        this.pdf_page_current--;
        returnthis.queueRenderPage(this.pdf_page_current);
    };

    /**
     *Displaysnextpage.
     */
    PDFSlidesViewer.prototype.nextPage=function(){
        if(this.pdf_page_current>=this.pdf_page_total){
            returnPromise.resolve(false);
        }
        this.pdf_page_current++;
        returnthis.queueRenderPage(this.pdf_page_current);
    };

    /*
     *Calculateascaletofitthedocumentontheavailablespace.
     */
    PDFSlidesViewer.prototype.getScaleToFit=function(page){
        varmaxWidth=this.canvas.parentNode.clientWidth;
        varmaxHeight=this.canvas.parentNode.clientHeight;
        varhScale=maxWidth/page.view[2];
        varvScale=maxHeight/page.view[3];
        returnMath.min(hScale,vScale);
    };

    /**
     *Displaysthegivenpage.
     */
    PDFSlidesViewer.prototype.changePage=function(num){
        if(1<=num<=this.pdf_page_total){
            this.pdf_page_current=num;
            returnthis.queueRenderPage(num);
        }
        returnPromise.resolve(false);
    }

    /**
     *Displaysfirstpage.
     */
    PDFSlidesViewer.prototype.firstPage=function(){
        this.pdf_page_current=1;
        returnthis.queueRenderPage(1);
    }

    /**
     *Displayslastpage.
     */
    PDFSlidesViewer.prototype.lastPage=function(){
        this.pdf_page_current=this.pdf_page_total;
        returnthis.queueRenderPage(this.pdf_page_total);
    }

    PDFSlidesViewer.prototype.toggleFullScreenFooter=function(){
        if(document.fullscreenElement||document.mozFullScreenElement||document.webkitFullscreenElement||document.msFullscreenElement){
            var$navBarFooter=$('div#PDFViewerdiv.oe_slides_panel_footer').parent();
            $navBarFooter.toggleClass('oe_show_footer');
            $navBarFooter.toggle();
        }
    }

    PDFSlidesViewer.prototype.toggleFullScreen=function(){
        //Thecanvasandthenavigationbarneedstobefullscreened
        varel=this.canvas.parentNode.parentNode;

        varisFullscreenAvailable=document.fullscreenEnabled||document.mozFullScreenEnabled||document.webkitFullscreenEnabled||document.msFullscreenEnabled||false;
        if(isFullscreenAvailable){//Fullscreensupported
            //gettheactualelementinFullScreenmode(Nullifnoelement)
            varfullscreenElement=document.fullscreenElement||document.mozFullScreenElement||document.webkitFullscreenElement||document.msFullscreenElement;

            if(fullscreenElement){//Exitthefullscreenmode
                if(document.exitFullscreen){
                    //W3Cstandard
                    document.exitFullscreen();
                }elseif(document.mozCancelFullScreen){
                    //Firefox10+,FirefoxforAndroid
                    document.mozCancelFullScreen();
                }elseif(document.webkitExitFullscreen){
                    //Chrome20+,Safari6+,Opera15+,ChromeforAndroid,OperaMobile16+
                    document.webkitExitFullscreen();
                }elseif(document.webkitCancelFullScreen){
                    //Chrome15+,Safari5.1+
                    document.webkitCancelFullScreen();
                }elseif(document.msExitFullscreen){
                    //IE11+
                    document.msExitFullscreen();
                }
            }else{//Requesttoputthe'el'elementinFullScreenmode
                if(el.requestFullscreen){
                    //W3Cstandard
                    el.requestFullscreen();
                }elseif(el.mozRequestFullScreen){
                    //Firefox10+,FirefoxforAndroid
                    el.mozRequestFullScreen();
                }elseif(el.msRequestFullscreen){
                    //IE11+
                    el.msRequestFullscreen();
                }elseif(el.webkitRequestFullscreen){
                    if(navigator.userAgent.indexOf('Safari')!=-1&&navigator.userAgent.indexOf('Chrome')==-1){
                        //Safari6+
                        el.webkitRequestFullscreen();
                    }else{
                        //Chrome20+,Opera15+,ChromeforAndroid,OperaMobile16+
                        el.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
                    }
                }elseif(el.webkitRequestFullScreen){
                    if(navigator.userAgent.indexOf('Safari')!=-1&&navigator.userAgent.indexOf('Chrome')==-1){
                        //Safari5.1+
                        el.webkitRequestFullScreen();
                    }else{
                        //Chrome15+
                        el.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT);
                    }
                }
            }
        }else{
            //Fullscreennotsupportedbythebrowser
            console.error("ERROR:fullscreennotsupportedbywebbrowser");
        }
    }
    returnPDFSlidesViewer;
})();
