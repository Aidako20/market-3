flectra.define('website_twitter.animation',function(require){
'usestrict';

varcore=require('web.core');
varpublicWidget=require('web.public.widget');

varqweb=core.qweb;

publicWidget.registry.twitter=publicWidget.Widget.extend({
    selector:'.twitter',
    xmlDependencies:['/website_twitter/static/src/xml/website.twitter.xml'],
    disabledInEditableMode:false,
    events:{
        'mouseenter.wrap-row':'_onEnterRow',
        'mouseleave.wrap-row':'_onLeaveRow',
        'click.twitter_timeline.tweet':'_onTweetClick',
    },

    /**
     *@override
     */
    start:function(){
        varself=this;
        var$timeline=this.$('.twitter_timeline');

        $timeline.append('<center><div><imgsrc="/website_twitter/static/src/img/loadtweet.gif"></div></center>');
        vardef=this._rpc({route:'/website_twitter/get_favorites'}).then(function(data){
            $timeline.empty();

            if(data.error){
                $timeline.append(qweb.render('website.Twitter.Error',{data:data}));
                return;
            }

            if(_.isEmpty(data)){
                return;
            }

            vartweets=_.map(data,function(tweet){
                //Parsetweetdate
                if(_.isEmpty(tweet.created_at)){
                    tweet.created_at='';
                }else{
                    varv=tweet.created_at.split('');
                    vard=newDate(Date.parse(v[1]+''+v[2]+','+v[5]+''+v[3]+'UTC'));
                    tweet.created_at=d.toDateString();
                }

                //Parsetweettext
                tweet.text=tweet.text
                    .replace(
                        /[A-Za-z]+:\/\/[A-Za-z0-9-_]+\.[A-Za-z0-9-_:%&~\?\/.=]+/g,
                        function(url){
                            return_makeLink(url,url);
                        }
                    )
                    .replace(
                        /[@]+[A-Za-z0-9_]+/g,
                        function(screen_name){
                            return_makeLink('http://twitter.com/'+screen_name.replace('@',''),screen_name);
                        }
                    )
                    .replace(
                        /[#]+[A-Za-z0-9_]+/g,
                        function(hashtag){
                            return_makeLink('http://twitter.com/search?q='+encodeURIComponent(hashtag.replace('#','')),hashtag);
                        }
                    );

                returnqweb.render('website.Twitter.Tweet',{tweet:tweet});

                function_makeLink(url,text){
                    varc=$('<a/>',{
                        text:text,
                        href:url,
                        target:'_blank',
                        rel:'noreferrernoopener',
                    });
                    returnc.prop('outerHTML');
                }
            });

            varf=Math.floor(tweets.length/3);
            vartweetSlices=[tweets.slice(0,f).join(''),tweets.slice(f,f*2).join(''),tweets.slice(f*2,tweets.length).join('')];

            self.$scroller=$(qweb.render('website.Twitter.Scroller')).appendTo($timeline);
            _.each(self.$scroller.find('div[id^="scroller"]'),function(element,index){
                var$scrollWrapper=$('<div/>',{class:'scrollWrapper'});
                var$scrollableArea=$('<div/>',{class:'scrollableArea'});
                $scrollWrapper.append($scrollableArea)
                              .data('scrollableArea',$scrollableArea);
                $scrollableArea.append(tweetSlices[index]);
                $(element).append($scrollWrapper);
                vartotalWidth=0;
                _.each($scrollableArea.children(),function(area){
                    totalWidth+=$(area).outerWidth(true);
                });
                $scrollableArea.width(totalWidth);
                $scrollWrapper.scrollLeft(index*180);
            });
            self._startScrolling();
        });

        returnPromise.all([this._super.apply(this,arguments),def]);
    },
    /**
     *@override
     */
    destroy:function(){
        this._stopScrolling();
        this._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _startScrolling:function(){
        if(!this.$scroller){
            return;
        }
        _.each(this.$scroller.find('.scrollWrapper'),function(el){
            var$wrapper=$(el);
            $wrapper.data('getNextElementWidth',true);
            $wrapper.data('autoScrollingInterval',setInterval(function(){
                $wrapper.scrollLeft($wrapper.scrollLeft()+1);
                if($wrapper.data('getNextElementWidth')){
                    $wrapper.data('swapAt',$wrapper.data('scrollableArea').children(':first').outerWidth(true));
                    $wrapper.data('getNextElementWidth',false);
                }
                if($wrapper.data('swapAt')<=$wrapper.scrollLeft()){
                    varswap_el=$wrapper.data('scrollableArea').children(':first').detach();
                    $wrapper.data('scrollableArea').append(swap_el);
                    $wrapper.scrollLeft($wrapper.scrollLeft()-swap_el.outerWidth(true));
                    $wrapper.data('getNextElementWidth',true);
                }
            },20));
        });
    },
    /**
     *@private
     */
    _stopScrolling:function(wrapper){
        if(!this.$scroller){
            return;
        }
        _.each(this.$scroller.find('.scrollWrapper'),function(el){
            var$wrapper=$(el);
            clearInterval($wrapper.data('autoScrollingInterval'));
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onEnterRow:function(){
        this._stopScrolling();
    },
    /**
     *@private
     */
    _onLeaveRow:function(){
        this._startScrolling();
    },
    /**
     *@private
     *@param{Event}ev
     */
    _onTweetClick:function(ev){
        if(ev.target.tagName==='A'){
            return;
        }
        varurl=$(ev.currentTarget).data('url');
        if(url){
            window.open(url,'_blank');
        }
    },
});
});
