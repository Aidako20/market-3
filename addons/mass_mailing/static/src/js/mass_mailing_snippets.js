flectra.define('mass_mailing.snippets.options',function(require){
"usestrict";

varoptions=require('web_editor.snippets.options');

//Snippetoptionforresizing imageandcolumnwidthinlinelikeexcel
options.registry.mass_mailing_sizing_x=options.Class.extend({
    /**
     *@override
     */
    start:function(){
        vardef=this._super.apply(this,arguments);

        this.containerWidth=this.$target.parent().closest("td,table,div").width();

        varself=this;
        varoffset,sib_offset,target_width,sib_width;

        this.$overlay.find(".o_handle.e,.o_handle.w").removeClass("readonly");
        this.isIMG=this.$target.is("img");
        if(this.isIMG){
            this.$overlay.find(".o_handle.w").addClass("readonly");
        }

        var$body=$(this.ownerDocument.body);
        this.$overlay.find(".o_handle").on('mousedown',function(event){
            event.preventDefault();
            var$handle=$(this);
            varcompass=false;

            _.each(['n','s','e','w'],function(handler){
                if($handle.hasClass(handler)){compass=handler;}
            });
            if(self.isIMG){compass="image";}

            $body.on("mousemove.mass_mailing_width_x",function(event){
                event.preventDefault();
                offset=self.$target.offset().left;
                target_width=self.get_max_width(self.$target);
                if(compass==='e'&&self.$target.next().offset()){
                    sib_width=self.get_max_width(self.$target.next());
                    sib_offset=self.$target.next().offset().left;
                    self.change_width(event,self.$target,target_width,offset,true);
                    self.change_width(event,self.$target.next(),sib_width,sib_offset,false);
                }
                if(compass==='w'&&self.$target.prev().offset()){
                    sib_width=self.get_max_width(self.$target.prev());
                    sib_offset=self.$target.prev().offset().left;
                    self.change_width(event,self.$target,target_width,offset,false);
                    self.change_width(event,self.$target.prev(),sib_width,sib_offset,true);
                }
                if(compass==='image'){
                    self.change_width(event,self.$target,target_width,offset,true);
                }
            });
            $body.one("mouseup",function(){
                $body.off('.mass_mailing_width_x');
            });
        });

        returndef;
    },
    change_width:function(event,target,target_width,offset,grow){
        target.css("width",grow?(event.pageX-offset):(offset+target_width-event.pageX));
        this.trigger_up('cover_update');
    },
    get_int_width:function(el){
        returnparseInt($(el).css("width"),10);
    },
    get_max_width:function($el){
        returnthis.containerWidth-_.reduce(_.map($el.siblings(),this.get_int_width),function(memo,w){returnmemo+w;});
    },
    onFocus:function(){
        this._super.apply(this,arguments);

        if(this.$target.is("td,th")){
            this.$overlay.find(".o_handle.e,.o_handle.w").toggleClass("readonly",this.$target.siblings().length===0);
        }
    },
});

options.registry.mass_mailing_table_item=options.Class.extend({
    onClone:function(options){
        this._super.apply(this,arguments);

        //Ifweclonedatdorthelement...
        if(options.isCurrent&&this.$target.is("td,th")){
            //...andthatthetdorthelementwasaloneonitsrow...
            if(this.$target.siblings().length===1){
                var$tr=this.$target.parent();
                $tr.clone().empty().insertAfter($tr).append(this.$target);//...movethecloneinanewrowinstead
                return;
            }

            //...ifnot,ifthecloneneighborisanemptycell,removethisemptycell(likeiftheclonecontenthadbeenputinthatcell)
            var$next=this.$target.next();
            if($next.length&&$next.text().trim()===""){
                $next.remove();
                return;
            }

            //...ifnot,insertanemptycolineachotherrow,attheindexoftheclone
            varwidth=this.$target.width();
            var$trs=this.$target.closest("table").children("thead,tbody,tfoot").addBack().children("tr").not(this.$target.parent());
            _.each($trs.children(":nth-child("+this.$target.index()+")"),function(col){
                $(col).after($("<td/>",{style:"width:"+width+"px;"}));
            });
        }
    },
    onRemove:function(){
        this._super.apply(this,arguments);

        //Ifweareremovingatdorthelementwhichwasnotaloneonitsrow...
        if(this.$target.is("td,th")&&this.$target.siblings().length>0){
            var$trs=this.$target.closest("table").children("thead,tbody,tfoot").addBack().children("tr").not(this.$target.parent());
            if($trs.length){//...ifthereareotherrowsinthetable...
                var$last_tds=$trs.children(":last-child");
                if(_.reduce($last_tds,function(memo,td){returnmemo+(td.innerHTML||"");},"").trim()===""){
                    $last_tds.remove();//...removethepotentialfullemptycolumninthetable
                }else{
                    this.$target.parent().append("<td/>");//...else,ifthereisnofullemptycolumn,appendanemptycolinthecurrentrow
                }
            }
        }
    },
});

//Addingcompatibilityfortheoutlookcomplianceofmailings.
//Commitofsuchcompatibility:a14f89c8663c9cafecb1cc26918055e023ecbe42
options.registry.BackgroundImage=options.registry.BackgroundImage.extend({
    start:function(){
        this._super();
        if(this.snippets&&this.snippets.split('.')[0]==="mass_mailing"){
            var$table_target=this.$target.find('table:first');
            if($table_target.length){
                this.$target=$table_target;
            }
        }
    }
});

//TODOremoveinmasterwhenremovingtheXMLdiv.Theoptionhasbeendisabled
//in14.0becauseoftrickyproblemstoresolvethatrequirerefactoring:
//theabilitytocleansnippetwithoutsavingandreloadingthepage.
options.registry.SnippetSave.include({

    asyncsaveSnippet(previewMode,widgetValue,params){},

    async_computeVisibility(){
        returnfalse;
    },
});
});
