//http://stackoverflow.com/questions/4383226/using-jquery-to-know-when-font-face-fonts-are-loaded
(function(){
    functionwaitForWebfonts(fonts,callback){
        varloadedFonts=0;
        for(vari=0,l=fonts.length;i<l;++i){
            (function(font){
                varnode=document.createElement('span');
                //Charactersthatvarysignificantlyamongdifferentfonts
                node.innerHTML='giItT1WQy@!-/#';
                //Visible-sowecanmeasureit-butnotonthescreen
                node.style.position     ='absolute';
                node.style.left         ='-10000px';
                node.style.top          ='-10000px';
                //Largefontsizemakesevensubtlechangesobvious
                node.style.fontSize     ='300px';
                //Resetanyfontproperties
                node.style.fontFamily   ='sans-serif';
                node.style.fontVariant  ='normal';
                node.style.fontStyle    ='normal';
                node.style.fontWeight   ='normal';
                node.style.letterSpacing='0';
                document.body.appendChild(node);

                //Rememberwidthwithnoappliedwebfont
                varwidth=node.offsetWidth;

                node.style.fontFamily=font;

                varinterval;
                functioncheckFont(){
                    //Comparecurrentwidthwithoriginalwidth
                    if(node&&node.offsetWidth!=width){
                        ++loadedFonts;
                        node.parentNode.removeChild(node);
                        node=null;
                    }

                    //Ifallfontshavebeenloaded
                    if(loadedFonts>=fonts.length){
                        if(interval){
                            clearInterval(interval);
                        }
                        if(loadedFonts==fonts.length){
                            callback();
                            returntrue;
                        }
                    }
                };

                if(!checkFont()){
                    interval=setInterval(checkFont,50);
                }
            })(fonts[i]);
        }
    }
    window.waitForWebfonts=waitForWebfonts;
})();


