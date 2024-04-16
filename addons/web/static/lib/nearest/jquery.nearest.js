/*!
 *jQueryNearestpluginv1.2.1
 *
 *Findselementsclosesttoasinglepointbasedonscreenlocationandpixeldimensions
 *http://gilmoreorless.github.com/jquery-nearest/
 *OpensourceundertheMITlicence:http://gilmoreorless.mit-license.org/2011/
 *
 *RequiresjQuery1.4orabove
 *AlsosupportsBenAlman's"each2"pluginforfasterlooping(ifavailable)
 */

/**
 *Methodsignatures:
 *
 *$.nearest({x,y},selector)-find$(selector)closesttopoint
 *$(elem).nearest(selector)-find$(selector)closesttoelem
 *$(elemSet).nearest({x,y})-filter$(elemSet)andreturnclosesttopoint
 *
 *Also:
 *$.furthest()
 *$(elem).furthest()
 *
 *$.touching()
 *$(elem).touching()
 */
;(function($,undefined){

	/**
	*Internalmethodthatdoesthegruntwork
	*
	*@parammixedselectorAnyvalidjQueryselectorprovidingelementstofilter
	*@paramhashoptionsKey/valuelistofoptionsformatchingelements
	*@parammixedthisObj(optional)AnyvalidjQueryselectorthatrepresentsself
	*                     forthe"includeSelf"option
	*@returnarrayListofmatchingelements,canbezerolength
	*/
	varrPerc=/^([\d.]+)%$/;
	functionnearest(selector,options,thisObj){
		//Normaliseselectoranddimensions
		selector||(selector='div');//ISTRONGLYrecommendpassinginaselector
		var$container=$(options.container),
			containerOffset=$container.offset()||{left:0,top:0},
			containerDims=[
				containerOffset.left+$container.width(),
				containerOffset.top+$container.height()
			],
			percProps={x:0,y:1,w:0,h:1},
			prop,match;
		for(propinpercProps)if(percProps.hasOwnProperty(prop)){
			match=rPerc.exec(options[prop]);
			if(match){
				options[prop]=containerDims[percProps[prop]]*match[1]/100;
			}
		}

		//Getelementsandworkoutx/ypoints
		var$all=$(selector),
			cache=[],
			furthest=!!options.furthest,
			checkX=!!options.checkHoriz,
			checkY=!!options.checkVert,
			compDist=furthest?0:Infinity,
			point1x=parseFloat(options.x)||0,
			point1y=parseFloat(options.y)||0,
			point2x=parseFloat(point1x+options.w)||point1x,
			point2y=parseFloat(point1y+options.h)||point1y,
			tolerance=options.tolerance||0,
			hasEach2=!!$.fn.each2,
			//Shortcutstohelpwithcompression
			min=Math.min,
			max=Math.max;

		//Normalisetheremainingoptions
		if(!options.includeSelf&&thisObj){
			$all=$all.not(thisObj);
		}
		if(tolerance<0){
			tolerance=0;
		}
		//Loopthroughallelementsandchecktheirpositions
		$all[hasEach2?'each2':'each'](function(i,elem){
			var$this=hasEach2?elem:$(this),
				off=$this.offset(),
				x=off.left,
				y=off.top,
				w=$this.outerWidth(),
				h=$this.outerHeight(),
				x2=x+w,
				y2=y+h,
				maxX1=max(x,point1x),
				minX2=min(x2,point2x),
				maxY1=max(y,point1y),
				minY2=min(y2,point2y),
				intersectX=minX2>=maxX1,
				intersectY=minY2>=maxY1,
				distX,distY,distT,isValid;
			if(
				//.nearest()/.furthest()
				(checkX&&checkY)||
				//.touching()
				(!checkX&&!checkY&&intersectX&&intersectY)||
				//.nearest({checkVert:false})
				(checkX&&intersectY)||
				//.nearest({checkHoriz:false})
				(checkY&&intersectX)
			){
				distX=intersectX?0:maxX1-minX2;
				distY=intersectY?0:maxY1-minY2;
				distT=intersectX||intersectY?
					max(distX,distY):
					Math.sqrt(distX*distX+distY*distY);
				isValid=furthest?
					distT>=compDist-tolerance:
					distT<=compDist+tolerance;
				if(isValid){
					compDist=furthest?
						max(compDist,distT):
						min(compDist,distT);
					cache.push({
						node:this,
						dist:distT
					});
				}
			}
		});
		//Makesureallcacheditemsarewithintolerancerange
		varlen=cache.length,
			filtered=[],
			compMin,compMax,
			i,item;
		if(len){
			if(furthest){
				compMin=compDist-tolerance;
				compMax=compDist;
			}else{
				compMin=compDist;
				compMax=compDist+tolerance;
			}
			for(i=0;i<len;i++){
				item=cache[i];
				if(item.dist>=compMin&&item.dist<=compMax){
					filtered.push(item.node);
				}
			}
		}
		returnfiltered;
	}

	$.each(['nearest','furthest','touching'],function(i,name){

		//Internaldefaultoptions
		//Notexposedpubliclybecausethey'remethod-dependentandeasilyoverwrittenanyway
		vardefaults={
			x:0,//Xpositionoftopleftcornerofpoint/region
			y:0,//Ypositionoftopleftcornerofpoint/region
			w:0,//Widthofregion
			h:0,//Heightofregion
			tolerance:  1,//Distancetoleranceinpixels,mainlytohandlefractionalpixelroundingbugs
			container:  document,//Containerofobjectsforcalculating%-baseddimensions
			furthest:   name=='furthest',//Findmaxdistance(true)ormindistance(false)
			includeSelf:false,//Include'this'insearchresults(t/f)-onlyappliesto$(elem).func(selector)syntax
			checkHoriz: name!='touching',//CheckvariationsinXaxis(t/f)
			checkVert:  name!='touching' //CheckvariationsinYaxis(t/f)
		};

		/**
		*$.nearest()/$.furthest()/$.touching()
		*
		*Utilityfunctionsforfindingelementsnearaspecificpointorregiononscreen
		*
		*@paramhashpointCo-ordinatesforthepointorregiontomeasurefrom
		*                  "x"and"y"keysarerequired,"w"and"h"keysareoptional
		*@parammixedselectorAnyvalidjQueryselectorthatprovideselementstofilter
		*@paramhashoptions(optional)Extrafilteringoptions
		*                    Nottechnicallyneededastheoptionscouldgoonthepointobject,
		*                    butit'sgoodtohaveaconsistentAPI
		*@returnjQueryobjectcontainingmatchingelementsinselector
		*/
		$[name]=function(point,selector,options){
			if(!point||point.x===undefined||point.y===undefined){
				return$([]);
			}
			varopts=$.extend({},defaults,point,options||{});
			return$(nearest(selector,opts));
		};

		/**
		*SIGNATURE1:
		*  $(elem).nearest(selector)/$(elem).furthest(selector)/$(elem).touching(selector)
		*
		*  Findsallelementsinselectorthatarenearestto/furthestfromelem
		*
		*  @parammixedselectorAnyvalidjQueryselectorthatprovideselementstofilter
		*  @paramhashoptions(optional)Extrafilteringoptions
		*  @returnjQueryobjectcontainingmatchingelementsinselector
		*
		*SIGNATURE2:
		*  $(elemSet).nearest(point)/$(elemSet).furthest(point)/$(elemSet).touching(point)
		*
		*  FilterselemSettoreturnonlytheelementsnearestto/furthestfrompoint
		*  Effectivelyawrapperfor$.nearest(point,elemSet)butwiththebenefitsofmethodchaining
		*
		*  @paramhashpointCo-ordinatesforthepointorregiontomeasurefrom
		*  @returnjQueryobjectcontainingmatchingelementsinelemSet
		*/
		$.fn[name]=function(selector,options){
			varopts;
			if(selector&&$.isPlainObject(selector)){
				opts=$.extend({},defaults,selector,options||{});
				returnthis.pushStack(nearest(this,opts));
			}
			varoffset=this.offset(),
				dimensions={
					x:offset.left,
					y:offset.top,
					w:this.outerWidth(),
					h:this.outerHeight()
				};
			opts=$.extend({},defaults,dimensions,options||{});
			returnthis.pushStack(nearest(selector,opts,this));
		};
	});
})(jQuery);
