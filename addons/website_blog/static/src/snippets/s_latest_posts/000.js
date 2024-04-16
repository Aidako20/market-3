flectra.define('website_blog.s_latest_posts_frontend',function(require){
'usestrict';

varcore=require('web.core');
varwUtils=require('website.utils');
varpublicWidget=require('web.public.widget');

var_t=core._t;

publicWidget.registry.js_get_posts=publicWidget.Widget.extend({
    selector:'.js_get_posts',
    disabledInEditableMode:false,

    /**
     *@override
     */
    start:function(){
        varself=this;
        constdata=self.$target[0].dataset;
        constlimit=parseInt(data.postsLimit)||4;
        constblogID=parseInt(data.filterByBlogId);
        //Compatibilitywitholdtemplatexmlid
        if(data.template&&data.template.endsWith('.s_latest_posts_big_orizontal_template')){
            data.template='website_blog.s_latest_posts_horizontal_template';
        }
        consttemplate=data.template||'website_blog.s_latest_posts_list_template';
        constloading=data.loading==='true';
        constorder=data.order||'published_datedesc';

        this.$target.empty();//Compatibilitywithdbthatsavedcontentinsidebymistake
        this.$target.attr('contenteditable','False');//Preventuseredition

        vardomain=[];
        if(blogID){
            domain.push(['blog_id','=',blogID]);
        }
        if(order.includes('visits')){
            domain.push(['visits','!=',false]);
        }

        varprom=newPromise(function(resolve){
            self._rpc({
                route:'/blog/render_latest_posts',
                params:{
                    template:template,
                    domain:domain,
                    limit:limit,
                    order:order,
                },
            }).then(function(posts){
                var$posts=$(posts).filter('.s_latest_posts_post');
                if(!$posts.length){
                    self.$target.append($('<div/>',{class:'col-md-6offset-md-3'})
                    .append($('<div/>',{
                        class:'alertalert-warningalert-dismissibletext-center',
                        text:_t("Noblogpostwasfound.Makesureyourpostsarepublished."),
                    })));
                    resolve();
                }

                if(loading){
                    //Performanintroanimation
                    self._showLoading($posts);
                }else{
                    self.$target.html($posts);
                }
                resolve();
            }).guardedCatch(function(){
                if(self.editableMode){
                    self.$target.append($('<p/>',{
                        class:'text-danger',
                        text:_t("Anerroroccuredwiththislatestpostsblock.Iftheproblempersists,pleaseconsiderdeletingitandaddinganewone"),
                    }));
                }
                resolve();
            });
        });
        returnPromise.all([this._super.apply(this,arguments),prom]);
    },
    /**
     *@override
     */
    destroy:function(){
        this.$target.empty();
        this._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _showLoading:function($posts){
        varself=this;

        _.each($posts,function(post,i){
            var$post=$(post);
            var$progress=$post.find('.s_latest_posts_loader');
            varbgUrl=$post.find('.o_record_cover_image').css('background-image').replace('url(','').replace(')','').replace(/\"/gi,"")||'none';

            //Append$posttothesnippet,regardlessbytheloadingstate.
            $post.appendTo(self.$target);

            //Nocover-imagefound.Adda'flag'classandexit.
            if(bgUrl==='none'){
                $post.addClass('s_latest_posts_loader_no_cover');
                $progress.remove();
                return;
            }

            //Coverimagefound.Showthespinningicon.
            $progress.find('>div').removeClass('d-none').css('animation-delay',i*200+'ms');
            var$dummyImg=$('<img/>',{src:bgUrl});

            //Iftheimageisnotloadedin10sec,removeloaderandprovideafallbackbg-colortothecontainer.
            //Hopefullyonedaytheimagewillload,coveringthebg-color...
            vartimer=setTimeout(function(){
                $post.find('.o_record_cover_image').addClass('bg-200');
                $progress.remove();
            },10000);

            wUtils.onceAllImagesLoaded($dummyImg).then(function(){
                $progress.fadeOut(500,function(){
                    $progress.removeClass('d-flex');
                });

                $dummyImg.remove();
                clearTimeout(timer);
            });
        });
    },
});
});
