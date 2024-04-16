/*!
 *Chart.jsv2.9.4
 *https://www.chartjs.org
 *(c)2020Chart.jsContributors
 *ReleasedundertheMITLicense
 */
(function(global,factory){
typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory(function(){try{returnrequire('moment');}catch(e){}}()):
typeofdefine==='function'&&define.amd?define(['require'],function(require){returnfactory(function(){try{returnrequire('moment');}catch(e){}}());}):
(global=global||self,global.Chart=factory(global.moment));
}(this,(function(moment){'usestrict';

moment=moment&&moment.hasOwnProperty('default')?moment['default']:moment;

functioncreateCommonjsModule(fn,module){
	returnmodule={exports:{}},fn(module,module.exports),module.exports;
}

functiongetCjsExportFromNamespace(n){
	returnn&&n['default']||n;
}

varcolorName={
	"aliceblue":[240,248,255],
	"antiquewhite":[250,235,215],
	"aqua":[0,255,255],
	"aquamarine":[127,255,212],
	"azure":[240,255,255],
	"beige":[245,245,220],
	"bisque":[255,228,196],
	"black":[0,0,0],
	"blanchedalmond":[255,235,205],
	"blue":[0,0,255],
	"blueviolet":[138,43,226],
	"brown":[165,42,42],
	"burlywood":[222,184,135],
	"cadetblue":[95,158,160],
	"chartreuse":[127,255,0],
	"chocolate":[210,105,30],
	"coral":[255,127,80],
	"cornflowerblue":[100,149,237],
	"cornsilk":[255,248,220],
	"crimson":[220,20,60],
	"cyan":[0,255,255],
	"darkblue":[0,0,139],
	"darkcyan":[0,139,139],
	"darkgoldenrod":[184,134,11],
	"darkgray":[169,169,169],
	"darkgreen":[0,100,0],
	"darkgrey":[169,169,169],
	"darkkhaki":[189,183,107],
	"darkmagenta":[139,0,139],
	"darkolivegreen":[85,107,47],
	"darkorange":[255,140,0],
	"darkorchid":[153,50,204],
	"darkred":[139,0,0],
	"darksalmon":[233,150,122],
	"darkseagreen":[143,188,143],
	"darkslateblue":[72,61,139],
	"darkslategray":[47,79,79],
	"darkslategrey":[47,79,79],
	"darkturquoise":[0,206,209],
	"darkviolet":[148,0,211],
	"deeppink":[255,20,147],
	"deepskyblue":[0,191,255],
	"dimgray":[105,105,105],
	"dimgrey":[105,105,105],
	"dodgerblue":[30,144,255],
	"firebrick":[178,34,34],
	"floralwhite":[255,250,240],
	"forestgreen":[34,139,34],
	"fuchsia":[255,0,255],
	"gainsboro":[220,220,220],
	"ghostwhite":[248,248,255],
	"gold":[255,215,0],
	"goldenrod":[218,165,32],
	"gray":[128,128,128],
	"green":[0,128,0],
	"greenyellow":[173,255,47],
	"grey":[128,128,128],
	"honeydew":[240,255,240],
	"hotpink":[255,105,180],
	"indianred":[205,92,92],
	"indigo":[75,0,130],
	"ivory":[255,255,240],
	"khaki":[240,230,140],
	"lavender":[230,230,250],
	"lavenderblush":[255,240,245],
	"lawngreen":[124,252,0],
	"lemonchiffon":[255,250,205],
	"lightblue":[173,216,230],
	"lightcoral":[240,128,128],
	"lightcyan":[224,255,255],
	"lightgoldenrodyellow":[250,250,210],
	"lightgray":[211,211,211],
	"lightgreen":[144,238,144],
	"lightgrey":[211,211,211],
	"lightpink":[255,182,193],
	"lightsalmon":[255,160,122],
	"lightseagreen":[32,178,170],
	"lightskyblue":[135,206,250],
	"lightslategray":[119,136,153],
	"lightslategrey":[119,136,153],
	"lightsteelblue":[176,196,222],
	"lightyellow":[255,255,224],
	"lime":[0,255,0],
	"limegreen":[50,205,50],
	"linen":[250,240,230],
	"magenta":[255,0,255],
	"maroon":[128,0,0],
	"mediumaquamarine":[102,205,170],
	"mediumblue":[0,0,205],
	"mediumorchid":[186,85,211],
	"mediumpurple":[147,112,219],
	"mediumseagreen":[60,179,113],
	"mediumslateblue":[123,104,238],
	"mediumspringgreen":[0,250,154],
	"mediumturquoise":[72,209,204],
	"mediumvioletred":[199,21,133],
	"midnightblue":[25,25,112],
	"mintcream":[245,255,250],
	"mistyrose":[255,228,225],
	"moccasin":[255,228,181],
	"navajowhite":[255,222,173],
	"navy":[0,0,128],
	"oldlace":[253,245,230],
	"olive":[128,128,0],
	"olivedrab":[107,142,35],
	"orange":[255,165,0],
	"orangered":[255,69,0],
	"orchid":[218,112,214],
	"palegoldenrod":[238,232,170],
	"palegreen":[152,251,152],
	"paleturquoise":[175,238,238],
	"palevioletred":[219,112,147],
	"papayawhip":[255,239,213],
	"peachpuff":[255,218,185],
	"peru":[205,133,63],
	"pink":[255,192,203],
	"plum":[221,160,221],
	"powderblue":[176,224,230],
	"purple":[128,0,128],
	"rebeccapurple":[102,51,153],
	"red":[255,0,0],
	"rosybrown":[188,143,143],
	"royalblue":[65,105,225],
	"saddlebrown":[139,69,19],
	"salmon":[250,128,114],
	"sandybrown":[244,164,96],
	"seagreen":[46,139,87],
	"seashell":[255,245,238],
	"sienna":[160,82,45],
	"silver":[192,192,192],
	"skyblue":[135,206,235],
	"slateblue":[106,90,205],
	"slategray":[112,128,144],
	"slategrey":[112,128,144],
	"snow":[255,250,250],
	"springgreen":[0,255,127],
	"steelblue":[70,130,180],
	"tan":[210,180,140],
	"teal":[0,128,128],
	"thistle":[216,191,216],
	"tomato":[255,99,71],
	"turquoise":[64,224,208],
	"violet":[238,130,238],
	"wheat":[245,222,179],
	"white":[255,255,255],
	"whitesmoke":[245,245,245],
	"yellow":[255,255,0],
	"yellowgreen":[154,205,50]
};

varconversions=createCommonjsModule(function(module){
/*MITlicense*/


//NOTE:conversionsshouldonlyreturnprimitivevalues(i.e.arrays,or
//      valuesthatgivecorrect`typeof`results).
//      donotuseboxvaluestypes(i.e.Number(),String(),etc.)

varreverseKeywords={};
for(varkeyincolorName){
	if(colorName.hasOwnProperty(key)){
		reverseKeywords[colorName[key]]=key;
	}
}

varconvert=module.exports={
	rgb:{channels:3,labels:'rgb'},
	hsl:{channels:3,labels:'hsl'},
	hsv:{channels:3,labels:'hsv'},
	hwb:{channels:3,labels:'hwb'},
	cmyk:{channels:4,labels:'cmyk'},
	xyz:{channels:3,labels:'xyz'},
	lab:{channels:3,labels:'lab'},
	lch:{channels:3,labels:'lch'},
	hex:{channels:1,labels:['hex']},
	keyword:{channels:1,labels:['keyword']},
	ansi16:{channels:1,labels:['ansi16']},
	ansi256:{channels:1,labels:['ansi256']},
	hcg:{channels:3,labels:['h','c','g']},
	apple:{channels:3,labels:['r16','g16','b16']},
	gray:{channels:1,labels:['gray']}
};

//hide.channelsand.labelsproperties
for(varmodelinconvert){
	if(convert.hasOwnProperty(model)){
		if(!('channels'inconvert[model])){
			thrownewError('missingchannelsproperty:'+model);
		}

		if(!('labels'inconvert[model])){
			thrownewError('missingchannellabelsproperty:'+model);
		}

		if(convert[model].labels.length!==convert[model].channels){
			thrownewError('channelandlabelcountsmismatch:'+model);
		}

		varchannels=convert[model].channels;
		varlabels=convert[model].labels;
		deleteconvert[model].channels;
		deleteconvert[model].labels;
		Object.defineProperty(convert[model],'channels',{value:channels});
		Object.defineProperty(convert[model],'labels',{value:labels});
	}
}

convert.rgb.hsl=function(rgb){
	varr=rgb[0]/255;
	varg=rgb[1]/255;
	varb=rgb[2]/255;
	varmin=Math.min(r,g,b);
	varmax=Math.max(r,g,b);
	vardelta=max-min;
	varh;
	vars;
	varl;

	if(max===min){
		h=0;
	}elseif(r===max){
		h=(g-b)/delta;
	}elseif(g===max){
		h=2+(b-r)/delta;
	}elseif(b===max){
		h=4+(r-g)/delta;
	}

	h=Math.min(h*60,360);

	if(h<0){
		h+=360;
	}

	l=(min+max)/2;

	if(max===min){
		s=0;
	}elseif(l<=0.5){
		s=delta/(max+min);
	}else{
		s=delta/(2-max-min);
	}

	return[h,s*100,l*100];
};

convert.rgb.hsv=function(rgb){
	varrdif;
	vargdif;
	varbdif;
	varh;
	vars;

	varr=rgb[0]/255;
	varg=rgb[1]/255;
	varb=rgb[2]/255;
	varv=Math.max(r,g,b);
	vardiff=v-Math.min(r,g,b);
	vardiffc=function(c){
		return(v-c)/6/diff+1/2;
	};

	if(diff===0){
		h=s=0;
	}else{
		s=diff/v;
		rdif=diffc(r);
		gdif=diffc(g);
		bdif=diffc(b);

		if(r===v){
			h=bdif-gdif;
		}elseif(g===v){
			h=(1/3)+rdif-bdif;
		}elseif(b===v){
			h=(2/3)+gdif-rdif;
		}
		if(h<0){
			h+=1;
		}elseif(h>1){
			h-=1;
		}
	}

	return[
		h*360,
		s*100,
		v*100
	];
};

convert.rgb.hwb=function(rgb){
	varr=rgb[0];
	varg=rgb[1];
	varb=rgb[2];
	varh=convert.rgb.hsl(rgb)[0];
	varw=1/255*Math.min(r,Math.min(g,b));

	b=1-1/255*Math.max(r,Math.max(g,b));

	return[h,w*100,b*100];
};

convert.rgb.cmyk=function(rgb){
	varr=rgb[0]/255;
	varg=rgb[1]/255;
	varb=rgb[2]/255;
	varc;
	varm;
	vary;
	vark;

	k=Math.min(1-r,1-g,1-b);
	c=(1-r-k)/(1-k)||0;
	m=(1-g-k)/(1-k)||0;
	y=(1-b-k)/(1-k)||0;

	return[c*100,m*100,y*100,k*100];
};

/**
 *Seehttps://en.m.wikipedia.org/wiki/Euclidean_distance#Squared_Euclidean_distance
 **/
functioncomparativeDistance(x,y){
	return(
		Math.pow(x[0]-y[0],2)+
		Math.pow(x[1]-y[1],2)+
		Math.pow(x[2]-y[2],2)
	);
}

convert.rgb.keyword=function(rgb){
	varreversed=reverseKeywords[rgb];
	if(reversed){
		returnreversed;
	}

	varcurrentClosestDistance=Infinity;
	varcurrentClosestKeyword;

	for(varkeywordincolorName){
		if(colorName.hasOwnProperty(keyword)){
			varvalue=colorName[keyword];

			//Computecomparativedistance
			vardistance=comparativeDistance(rgb,value);

			//Checkifitsless,ifsosetasclosest
			if(distance<currentClosestDistance){
				currentClosestDistance=distance;
				currentClosestKeyword=keyword;
			}
		}
	}

	returncurrentClosestKeyword;
};

convert.keyword.rgb=function(keyword){
	returncolorName[keyword];
};

convert.rgb.xyz=function(rgb){
	varr=rgb[0]/255;
	varg=rgb[1]/255;
	varb=rgb[2]/255;

	//assumesRGB
	r=r>0.04045?Math.pow(((r+0.055)/1.055),2.4):(r/12.92);
	g=g>0.04045?Math.pow(((g+0.055)/1.055),2.4):(g/12.92);
	b=b>0.04045?Math.pow(((b+0.055)/1.055),2.4):(b/12.92);

	varx=(r*0.4124)+(g*0.3576)+(b*0.1805);
	vary=(r*0.2126)+(g*0.7152)+(b*0.0722);
	varz=(r*0.0193)+(g*0.1192)+(b*0.9505);

	return[x*100,y*100,z*100];
};

convert.rgb.lab=function(rgb){
	varxyz=convert.rgb.xyz(rgb);
	varx=xyz[0];
	vary=xyz[1];
	varz=xyz[2];
	varl;
	vara;
	varb;

	x/=95.047;
	y/=100;
	z/=108.883;

	x=x>0.008856?Math.pow(x,1/3):(7.787*x)+(16/116);
	y=y>0.008856?Math.pow(y,1/3):(7.787*y)+(16/116);
	z=z>0.008856?Math.pow(z,1/3):(7.787*z)+(16/116);

	l=(116*y)-16;
	a=500*(x-y);
	b=200*(y-z);

	return[l,a,b];
};

convert.hsl.rgb=function(hsl){
	varh=hsl[0]/360;
	vars=hsl[1]/100;
	varl=hsl[2]/100;
	vart1;
	vart2;
	vart3;
	varrgb;
	varval;

	if(s===0){
		val=l*255;
		return[val,val,val];
	}

	if(l<0.5){
		t2=l*(1+s);
	}else{
		t2=l+s-l*s;
	}

	t1=2*l-t2;

	rgb=[0,0,0];
	for(vari=0;i<3;i++){
		t3=h+1/3*-(i-1);
		if(t3<0){
			t3++;
		}
		if(t3>1){
			t3--;
		}

		if(6*t3<1){
			val=t1+(t2-t1)*6*t3;
		}elseif(2*t3<1){
			val=t2;
		}elseif(3*t3<2){
			val=t1+(t2-t1)*(2/3-t3)*6;
		}else{
			val=t1;
		}

		rgb[i]=val*255;
	}

	returnrgb;
};

convert.hsl.hsv=function(hsl){
	varh=hsl[0];
	vars=hsl[1]/100;
	varl=hsl[2]/100;
	varsmin=s;
	varlmin=Math.max(l,0.01);
	varsv;
	varv;

	l*=2;
	s*=(l<=1)?l:2-l;
	smin*=lmin<=1?lmin:2-lmin;
	v=(l+s)/2;
	sv=l===0?(2*smin)/(lmin+smin):(2*s)/(l+s);

	return[h,sv*100,v*100];
};

convert.hsv.rgb=function(hsv){
	varh=hsv[0]/60;
	vars=hsv[1]/100;
	varv=hsv[2]/100;
	varhi=Math.floor(h)%6;

	varf=h-Math.floor(h);
	varp=255*v*(1-s);
	varq=255*v*(1-(s*f));
	vart=255*v*(1-(s*(1-f)));
	v*=255;

	switch(hi){
		case0:
			return[v,t,p];
		case1:
			return[q,v,p];
		case2:
			return[p,v,t];
		case3:
			return[p,q,v];
		case4:
			return[t,p,v];
		case5:
			return[v,p,q];
	}
};

convert.hsv.hsl=function(hsv){
	varh=hsv[0];
	vars=hsv[1]/100;
	varv=hsv[2]/100;
	varvmin=Math.max(v,0.01);
	varlmin;
	varsl;
	varl;

	l=(2-s)*v;
	lmin=(2-s)*vmin;
	sl=s*vmin;
	sl/=(lmin<=1)?lmin:2-lmin;
	sl=sl||0;
	l/=2;

	return[h,sl*100,l*100];
};

//http://dev.w3.org/csswg/css-color/#hwb-to-rgb
convert.hwb.rgb=function(hwb){
	varh=hwb[0]/360;
	varwh=hwb[1]/100;
	varbl=hwb[2]/100;
	varratio=wh+bl;
	vari;
	varv;
	varf;
	varn;

	//wh+blcantbe>1
	if(ratio>1){
		wh/=ratio;
		bl/=ratio;
	}

	i=Math.floor(6*h);
	v=1-bl;
	f=6*h-i;

	if((i&0x01)!==0){
		f=1-f;
	}

	n=wh+f*(v-wh);//linearinterpolation

	varr;
	varg;
	varb;
	switch(i){
		default:
		case6:
		case0:r=v;g=n;b=wh;break;
		case1:r=n;g=v;b=wh;break;
		case2:r=wh;g=v;b=n;break;
		case3:r=wh;g=n;b=v;break;
		case4:r=n;g=wh;b=v;break;
		case5:r=v;g=wh;b=n;break;
	}

	return[r*255,g*255,b*255];
};

convert.cmyk.rgb=function(cmyk){
	varc=cmyk[0]/100;
	varm=cmyk[1]/100;
	vary=cmyk[2]/100;
	vark=cmyk[3]/100;
	varr;
	varg;
	varb;

	r=1-Math.min(1,c*(1-k)+k);
	g=1-Math.min(1,m*(1-k)+k);
	b=1-Math.min(1,y*(1-k)+k);

	return[r*255,g*255,b*255];
};

convert.xyz.rgb=function(xyz){
	varx=xyz[0]/100;
	vary=xyz[1]/100;
	varz=xyz[2]/100;
	varr;
	varg;
	varb;

	r=(x*3.2406)+(y*-1.5372)+(z*-0.4986);
	g=(x*-0.9689)+(y*1.8758)+(z*0.0415);
	b=(x*0.0557)+(y*-0.2040)+(z*1.0570);

	//assumesRGB
	r=r>0.0031308
		?((1.055*Math.pow(r,1.0/2.4))-0.055)
		:r*12.92;

	g=g>0.0031308
		?((1.055*Math.pow(g,1.0/2.4))-0.055)
		:g*12.92;

	b=b>0.0031308
		?((1.055*Math.pow(b,1.0/2.4))-0.055)
		:b*12.92;

	r=Math.min(Math.max(0,r),1);
	g=Math.min(Math.max(0,g),1);
	b=Math.min(Math.max(0,b),1);

	return[r*255,g*255,b*255];
};

convert.xyz.lab=function(xyz){
	varx=xyz[0];
	vary=xyz[1];
	varz=xyz[2];
	varl;
	vara;
	varb;

	x/=95.047;
	y/=100;
	z/=108.883;

	x=x>0.008856?Math.pow(x,1/3):(7.787*x)+(16/116);
	y=y>0.008856?Math.pow(y,1/3):(7.787*y)+(16/116);
	z=z>0.008856?Math.pow(z,1/3):(7.787*z)+(16/116);

	l=(116*y)-16;
	a=500*(x-y);
	b=200*(y-z);

	return[l,a,b];
};

convert.lab.xyz=function(lab){
	varl=lab[0];
	vara=lab[1];
	varb=lab[2];
	varx;
	vary;
	varz;

	y=(l+16)/116;
	x=a/500+y;
	z=y-b/200;

	vary2=Math.pow(y,3);
	varx2=Math.pow(x,3);
	varz2=Math.pow(z,3);
	y=y2>0.008856?y2:(y-16/116)/7.787;
	x=x2>0.008856?x2:(x-16/116)/7.787;
	z=z2>0.008856?z2:(z-16/116)/7.787;

	x*=95.047;
	y*=100;
	z*=108.883;

	return[x,y,z];
};

convert.lab.lch=function(lab){
	varl=lab[0];
	vara=lab[1];
	varb=lab[2];
	varhr;
	varh;
	varc;

	hr=Math.atan2(b,a);
	h=hr*360/2/Math.PI;

	if(h<0){
		h+=360;
	}

	c=Math.sqrt(a*a+b*b);

	return[l,c,h];
};

convert.lch.lab=function(lch){
	varl=lch[0];
	varc=lch[1];
	varh=lch[2];
	vara;
	varb;
	varhr;

	hr=h/360*2*Math.PI;
	a=c*Math.cos(hr);
	b=c*Math.sin(hr);

	return[l,a,b];
};

convert.rgb.ansi16=function(args){
	varr=args[0];
	varg=args[1];
	varb=args[2];
	varvalue=1inarguments?arguments[1]:convert.rgb.hsv(args)[2];//hsv->ansi16optimization

	value=Math.round(value/50);

	if(value===0){
		return30;
	}

	varansi=30
		+((Math.round(b/255)<<2)
		|(Math.round(g/255)<<1)
		|Math.round(r/255));

	if(value===2){
		ansi+=60;
	}

	returnansi;
};

convert.hsv.ansi16=function(args){
	//optimizationhere;wealreadyknowthevalueanddon'tneedtoget
	//itconvertedforus.
	returnconvert.rgb.ansi16(convert.hsv.rgb(args),args[2]);
};

convert.rgb.ansi256=function(args){
	varr=args[0];
	varg=args[1];
	varb=args[2];

	//weusetheextendedgreyscalepalettehere,withtheexceptionof
	//blackandwhite.normalpaletteonlyhas4greyscaleshades.
	if(r===g&&g===b){
		if(r<8){
			return16;
		}

		if(r>248){
			return231;
		}

		returnMath.round(((r-8)/247)*24)+232;
	}

	varansi=16
		+(36*Math.round(r/255*5))
		+(6*Math.round(g/255*5))
		+Math.round(b/255*5);

	returnansi;
};

convert.ansi16.rgb=function(args){
	varcolor=args%10;

	//handlegreyscale
	if(color===0||color===7){
		if(args>50){
			color+=3.5;
		}

		color=color/10.5*255;

		return[color,color,color];
	}

	varmult=(~~(args>50)+1)*0.5;
	varr=((color&1)*mult)*255;
	varg=(((color>>1)&1)*mult)*255;
	varb=(((color>>2)&1)*mult)*255;

	return[r,g,b];
};

convert.ansi256.rgb=function(args){
	//handlegreyscale
	if(args>=232){
		varc=(args-232)*10+8;
		return[c,c,c];
	}

	args-=16;

	varrem;
	varr=Math.floor(args/36)/5*255;
	varg=Math.floor((rem=args%36)/6)/5*255;
	varb=(rem%6)/5*255;

	return[r,g,b];
};

convert.rgb.hex=function(args){
	varinteger=((Math.round(args[0])&0xFF)<<16)
		+((Math.round(args[1])&0xFF)<<8)
		+(Math.round(args[2])&0xFF);

	varstring=integer.toString(16).toUpperCase();
	return'000000'.substring(string.length)+string;
};

convert.hex.rgb=function(args){
	varmatch=args.toString(16).match(/[a-f0-9]{6}|[a-f0-9]{3}/i);
	if(!match){
		return[0,0,0];
	}

	varcolorString=match[0];

	if(match[0].length===3){
		colorString=colorString.split('').map(function(char){
			returnchar+char;
		}).join('');
	}

	varinteger=parseInt(colorString,16);
	varr=(integer>>16)&0xFF;
	varg=(integer>>8)&0xFF;
	varb=integer&0xFF;

	return[r,g,b];
};

convert.rgb.hcg=function(rgb){
	varr=rgb[0]/255;
	varg=rgb[1]/255;
	varb=rgb[2]/255;
	varmax=Math.max(Math.max(r,g),b);
	varmin=Math.min(Math.min(r,g),b);
	varchroma=(max-min);
	vargrayscale;
	varhue;

	if(chroma<1){
		grayscale=min/(1-chroma);
	}else{
		grayscale=0;
	}

	if(chroma<=0){
		hue=0;
	}else
	if(max===r){
		hue=((g-b)/chroma)%6;
	}else
	if(max===g){
		hue=2+(b-r)/chroma;
	}else{
		hue=4+(r-g)/chroma+4;
	}

	hue/=6;
	hue%=1;

	return[hue*360,chroma*100,grayscale*100];
};

convert.hsl.hcg=function(hsl){
	vars=hsl[1]/100;
	varl=hsl[2]/100;
	varc=1;
	varf=0;

	if(l<0.5){
		c=2.0*s*l;
	}else{
		c=2.0*s*(1.0-l);
	}

	if(c<1.0){
		f=(l-0.5*c)/(1.0-c);
	}

	return[hsl[0],c*100,f*100];
};

convert.hsv.hcg=function(hsv){
	vars=hsv[1]/100;
	varv=hsv[2]/100;

	varc=s*v;
	varf=0;

	if(c<1.0){
		f=(v-c)/(1-c);
	}

	return[hsv[0],c*100,f*100];
};

convert.hcg.rgb=function(hcg){
	varh=hcg[0]/360;
	varc=hcg[1]/100;
	varg=hcg[2]/100;

	if(c===0.0){
		return[g*255,g*255,g*255];
	}

	varpure=[0,0,0];
	varhi=(h%1)*6;
	varv=hi%1;
	varw=1-v;
	varmg=0;

	switch(Math.floor(hi)){
		case0:
			pure[0]=1;pure[1]=v;pure[2]=0;break;
		case1:
			pure[0]=w;pure[1]=1;pure[2]=0;break;
		case2:
			pure[0]=0;pure[1]=1;pure[2]=v;break;
		case3:
			pure[0]=0;pure[1]=w;pure[2]=1;break;
		case4:
			pure[0]=v;pure[1]=0;pure[2]=1;break;
		default:
			pure[0]=1;pure[1]=0;pure[2]=w;
	}

	mg=(1.0-c)*g;

	return[
		(c*pure[0]+mg)*255,
		(c*pure[1]+mg)*255,
		(c*pure[2]+mg)*255
	];
};

convert.hcg.hsv=function(hcg){
	varc=hcg[1]/100;
	varg=hcg[2]/100;

	varv=c+g*(1.0-c);
	varf=0;

	if(v>0.0){
		f=c/v;
	}

	return[hcg[0],f*100,v*100];
};

convert.hcg.hsl=function(hcg){
	varc=hcg[1]/100;
	varg=hcg[2]/100;

	varl=g*(1.0-c)+0.5*c;
	vars=0;

	if(l>0.0&&l<0.5){
		s=c/(2*l);
	}else
	if(l>=0.5&&l<1.0){
		s=c/(2*(1-l));
	}

	return[hcg[0],s*100,l*100];
};

convert.hcg.hwb=function(hcg){
	varc=hcg[1]/100;
	varg=hcg[2]/100;
	varv=c+g*(1.0-c);
	return[hcg[0],(v-c)*100,(1-v)*100];
};

convert.hwb.hcg=function(hwb){
	varw=hwb[1]/100;
	varb=hwb[2]/100;
	varv=1-b;
	varc=v-w;
	varg=0;

	if(c<1){
		g=(v-c)/(1-c);
	}

	return[hwb[0],c*100,g*100];
};

convert.apple.rgb=function(apple){
	return[(apple[0]/65535)*255,(apple[1]/65535)*255,(apple[2]/65535)*255];
};

convert.rgb.apple=function(rgb){
	return[(rgb[0]/255)*65535,(rgb[1]/255)*65535,(rgb[2]/255)*65535];
};

convert.gray.rgb=function(args){
	return[args[0]/100*255,args[0]/100*255,args[0]/100*255];
};

convert.gray.hsl=convert.gray.hsv=function(args){
	return[0,0,args[0]];
};

convert.gray.hwb=function(gray){
	return[0,100,gray[0]];
};

convert.gray.cmyk=function(gray){
	return[0,0,0,gray[0]];
};

convert.gray.lab=function(gray){
	return[gray[0],0,0];
};

convert.gray.hex=function(gray){
	varval=Math.round(gray[0]/100*255)&0xFF;
	varinteger=(val<<16)+(val<<8)+val;

	varstring=integer.toString(16).toUpperCase();
	return'000000'.substring(string.length)+string;
};

convert.rgb.gray=function(rgb){
	varval=(rgb[0]+rgb[1]+rgb[2])/3;
	return[val/255*100];
};
});
varconversions_1=conversions.rgb;
varconversions_2=conversions.hsl;
varconversions_3=conversions.hsv;
varconversions_4=conversions.hwb;
varconversions_5=conversions.cmyk;
varconversions_6=conversions.xyz;
varconversions_7=conversions.lab;
varconversions_8=conversions.lch;
varconversions_9=conversions.hex;
varconversions_10=conversions.keyword;
varconversions_11=conversions.ansi16;
varconversions_12=conversions.ansi256;
varconversions_13=conversions.hcg;
varconversions_14=conversions.apple;
varconversions_15=conversions.gray;

/*
	thisfunctionroutesamodeltoallothermodels.

	allfunctionsthatareroutedhaveaproperty`.conversion`attached
	tothereturnedsyntheticfunction.Thispropertyisanarray
	ofstrings,eachwiththestepsinbetweenthe'from'and'to'
	colormodels(inclusive).

	conversionsthatarenotpossiblesimplyarenotincluded.
*/

functionbuildGraph(){
	vargraph={};
	//https://jsperf.com/object-keys-vs-for-in-with-closure/3
	varmodels=Object.keys(conversions);

	for(varlen=models.length,i=0;i<len;i++){
		graph[models[i]]={
			//http://jsperf.com/1-vs-infinity
			//micro-opt,butthisissimple.
			distance:-1,
			parent:null
		};
	}

	returngraph;
}

//https://en.wikipedia.org/wiki/Breadth-first_search
functionderiveBFS(fromModel){
	vargraph=buildGraph();
	varqueue=[fromModel];//unshift->queue->pop

	graph[fromModel].distance=0;

	while(queue.length){
		varcurrent=queue.pop();
		varadjacents=Object.keys(conversions[current]);

		for(varlen=adjacents.length,i=0;i<len;i++){
			varadjacent=adjacents[i];
			varnode=graph[adjacent];

			if(node.distance===-1){
				node.distance=graph[current].distance+1;
				node.parent=current;
				queue.unshift(adjacent);
			}
		}
	}

	returngraph;
}

functionlink(from,to){
	returnfunction(args){
		returnto(from(args));
	};
}

functionwrapConversion(toModel,graph){
	varpath=[graph[toModel].parent,toModel];
	varfn=conversions[graph[toModel].parent][toModel];

	varcur=graph[toModel].parent;
	while(graph[cur].parent){
		path.unshift(graph[cur].parent);
		fn=link(conversions[graph[cur].parent][cur],fn);
		cur=graph[cur].parent;
	}

	fn.conversion=path;
	returnfn;
}

varroute=function(fromModel){
	vargraph=deriveBFS(fromModel);
	varconversion={};

	varmodels=Object.keys(graph);
	for(varlen=models.length,i=0;i<len;i++){
		vartoModel=models[i];
		varnode=graph[toModel];

		if(node.parent===null){
			//nopossibleconversion,orthisnodeisthesourcemodel.
			continue;
		}

		conversion[toModel]=wrapConversion(toModel,graph);
	}

	returnconversion;
};

varconvert={};

varmodels=Object.keys(conversions);

functionwrapRaw(fn){
	varwrappedFn=function(args){
		if(args===undefined||args===null){
			returnargs;
		}

		if(arguments.length>1){
			args=Array.prototype.slice.call(arguments);
		}

		returnfn(args);
	};

	//preserve.conversionpropertyifthereisone
	if('conversion'infn){
		wrappedFn.conversion=fn.conversion;
	}

	returnwrappedFn;
}

functionwrapRounded(fn){
	varwrappedFn=function(args){
		if(args===undefined||args===null){
			returnargs;
		}

		if(arguments.length>1){
			args=Array.prototype.slice.call(arguments);
		}

		varresult=fn(args);

		//we'reassumingtheresultisanarrayhere.
		//seenoticeinconversions.js;don'tuseboxtypes
		//inconversionfunctions.
		if(typeofresult==='object'){
			for(varlen=result.length,i=0;i<len;i++){
				result[i]=Math.round(result[i]);
			}
		}

		returnresult;
	};

	//preserve.conversionpropertyifthereisone
	if('conversion'infn){
		wrappedFn.conversion=fn.conversion;
	}

	returnwrappedFn;
}

models.forEach(function(fromModel){
	convert[fromModel]={};

	Object.defineProperty(convert[fromModel],'channels',{value:conversions[fromModel].channels});
	Object.defineProperty(convert[fromModel],'labels',{value:conversions[fromModel].labels});

	varroutes=route(fromModel);
	varrouteModels=Object.keys(routes);

	routeModels.forEach(function(toModel){
		varfn=routes[toModel];

		convert[fromModel][toModel]=wrapRounded(fn);
		convert[fromModel][toModel].raw=wrapRaw(fn);
	});
});

varcolorConvert=convert;

varcolorName$1={
	"aliceblue":[240,248,255],
	"antiquewhite":[250,235,215],
	"aqua":[0,255,255],
	"aquamarine":[127,255,212],
	"azure":[240,255,255],
	"beige":[245,245,220],
	"bisque":[255,228,196],
	"black":[0,0,0],
	"blanchedalmond":[255,235,205],
	"blue":[0,0,255],
	"blueviolet":[138,43,226],
	"brown":[165,42,42],
	"burlywood":[222,184,135],
	"cadetblue":[95,158,160],
	"chartreuse":[127,255,0],
	"chocolate":[210,105,30],
	"coral":[255,127,80],
	"cornflowerblue":[100,149,237],
	"cornsilk":[255,248,220],
	"crimson":[220,20,60],
	"cyan":[0,255,255],
	"darkblue":[0,0,139],
	"darkcyan":[0,139,139],
	"darkgoldenrod":[184,134,11],
	"darkgray":[169,169,169],
	"darkgreen":[0,100,0],
	"darkgrey":[169,169,169],
	"darkkhaki":[189,183,107],
	"darkmagenta":[139,0,139],
	"darkolivegreen":[85,107,47],
	"darkorange":[255,140,0],
	"darkorchid":[153,50,204],
	"darkred":[139,0,0],
	"darksalmon":[233,150,122],
	"darkseagreen":[143,188,143],
	"darkslateblue":[72,61,139],
	"darkslategray":[47,79,79],
	"darkslategrey":[47,79,79],
	"darkturquoise":[0,206,209],
	"darkviolet":[148,0,211],
	"deeppink":[255,20,147],
	"deepskyblue":[0,191,255],
	"dimgray":[105,105,105],
	"dimgrey":[105,105,105],
	"dodgerblue":[30,144,255],
	"firebrick":[178,34,34],
	"floralwhite":[255,250,240],
	"forestgreen":[34,139,34],
	"fuchsia":[255,0,255],
	"gainsboro":[220,220,220],
	"ghostwhite":[248,248,255],
	"gold":[255,215,0],
	"goldenrod":[218,165,32],
	"gray":[128,128,128],
	"green":[0,128,0],
	"greenyellow":[173,255,47],
	"grey":[128,128,128],
	"honeydew":[240,255,240],
	"hotpink":[255,105,180],
	"indianred":[205,92,92],
	"indigo":[75,0,130],
	"ivory":[255,255,240],
	"khaki":[240,230,140],
	"lavender":[230,230,250],
	"lavenderblush":[255,240,245],
	"lawngreen":[124,252,0],
	"lemonchiffon":[255,250,205],
	"lightblue":[173,216,230],
	"lightcoral":[240,128,128],
	"lightcyan":[224,255,255],
	"lightgoldenrodyellow":[250,250,210],
	"lightgray":[211,211,211],
	"lightgreen":[144,238,144],
	"lightgrey":[211,211,211],
	"lightpink":[255,182,193],
	"lightsalmon":[255,160,122],
	"lightseagreen":[32,178,170],
	"lightskyblue":[135,206,250],
	"lightslategray":[119,136,153],
	"lightslategrey":[119,136,153],
	"lightsteelblue":[176,196,222],
	"lightyellow":[255,255,224],
	"lime":[0,255,0],
	"limegreen":[50,205,50],
	"linen":[250,240,230],
	"magenta":[255,0,255],
	"maroon":[128,0,0],
	"mediumaquamarine":[102,205,170],
	"mediumblue":[0,0,205],
	"mediumorchid":[186,85,211],
	"mediumpurple":[147,112,219],
	"mediumseagreen":[60,179,113],
	"mediumslateblue":[123,104,238],
	"mediumspringgreen":[0,250,154],
	"mediumturquoise":[72,209,204],
	"mediumvioletred":[199,21,133],
	"midnightblue":[25,25,112],
	"mintcream":[245,255,250],
	"mistyrose":[255,228,225],
	"moccasin":[255,228,181],
	"navajowhite":[255,222,173],
	"navy":[0,0,128],
	"oldlace":[253,245,230],
	"olive":[128,128,0],
	"olivedrab":[107,142,35],
	"orange":[255,165,0],
	"orangered":[255,69,0],
	"orchid":[218,112,214],
	"palegoldenrod":[238,232,170],
	"palegreen":[152,251,152],
	"paleturquoise":[175,238,238],
	"palevioletred":[219,112,147],
	"papayawhip":[255,239,213],
	"peachpuff":[255,218,185],
	"peru":[205,133,63],
	"pink":[255,192,203],
	"plum":[221,160,221],
	"powderblue":[176,224,230],
	"purple":[128,0,128],
	"rebeccapurple":[102,51,153],
	"red":[255,0,0],
	"rosybrown":[188,143,143],
	"royalblue":[65,105,225],
	"saddlebrown":[139,69,19],
	"salmon":[250,128,114],
	"sandybrown":[244,164,96],
	"seagreen":[46,139,87],
	"seashell":[255,245,238],
	"sienna":[160,82,45],
	"silver":[192,192,192],
	"skyblue":[135,206,235],
	"slateblue":[106,90,205],
	"slategray":[112,128,144],
	"slategrey":[112,128,144],
	"snow":[255,250,250],
	"springgreen":[0,255,127],
	"steelblue":[70,130,180],
	"tan":[210,180,140],
	"teal":[0,128,128],
	"thistle":[216,191,216],
	"tomato":[255,99,71],
	"turquoise":[64,224,208],
	"violet":[238,130,238],
	"wheat":[245,222,179],
	"white":[255,255,255],
	"whitesmoke":[245,245,245],
	"yellow":[255,255,0],
	"yellowgreen":[154,205,50]
};

/*MITlicense*/


varcolorString={
   getRgba:getRgba,
   getHsla:getHsla,
   getRgb:getRgb,
   getHsl:getHsl,
   getHwb:getHwb,
   getAlpha:getAlpha,

   hexString:hexString,
   rgbString:rgbString,
   rgbaString:rgbaString,
   percentString:percentString,
   percentaString:percentaString,
   hslString:hslString,
   hslaString:hslaString,
   hwbString:hwbString,
   keyword:keyword
};

functiongetRgba(string){
   if(!string){
      return;
   }
   varabbr= /^#([a-fA-F0-9]{3,4})$/i,
       hex= /^#([a-fA-F0-9]{6}([a-fA-F0-9]{2})?)$/i,
       rgba=/^rgba?\(\s*([+-]?\d+)\s*,\s*([+-]?\d+)\s*,\s*([+-]?\d+)\s*(?:,\s*([+-]?[\d\.]+)\s*)?\)$/i,
       per=/^rgba?\(\s*([+-]?[\d\.]+)\%\s*,\s*([+-]?[\d\.]+)\%\s*,\s*([+-]?[\d\.]+)\%\s*(?:,\s*([+-]?[\d\.]+)\s*)?\)$/i,
       keyword=/(\w+)/;

   varrgb=[0,0,0],
       a=1,
       match=string.match(abbr),
       hexAlpha="";
   if(match){
      match=match[1];
      hexAlpha=match[3];
      for(vari=0;i<rgb.length;i++){
         rgb[i]=parseInt(match[i]+match[i],16);
      }
      if(hexAlpha){
         a=Math.round((parseInt(hexAlpha+hexAlpha,16)/255)*100)/100;
      }
   }
   elseif(match=string.match(hex)){
      hexAlpha=match[2];
      match=match[1];
      for(vari=0;i<rgb.length;i++){
         rgb[i]=parseInt(match.slice(i*2,i*2+2),16);
      }
      if(hexAlpha){
         a=Math.round((parseInt(hexAlpha,16)/255)*100)/100;
      }
   }
   elseif(match=string.match(rgba)){
      for(vari=0;i<rgb.length;i++){
         rgb[i]=parseInt(match[i+1]);
      }
      a=parseFloat(match[4]);
   }
   elseif(match=string.match(per)){
      for(vari=0;i<rgb.length;i++){
         rgb[i]=Math.round(parseFloat(match[i+1])*2.55);
      }
      a=parseFloat(match[4]);
   }
   elseif(match=string.match(keyword)){
      if(match[1]=="transparent"){
         return[0,0,0,0];
      }
      rgb=colorName$1[match[1]];
      if(!rgb){
         return;
      }
   }

   for(vari=0;i<rgb.length;i++){
      rgb[i]=scale(rgb[i],0,255);
   }
   if(!a&&a!=0){
      a=1;
   }
   else{
      a=scale(a,0,1);
   }
   rgb[3]=a;
   returnrgb;
}

functiongetHsla(string){
   if(!string){
      return;
   }
   varhsl=/^hsla?\(\s*([+-]?\d+)(?:deg)?\s*,\s*([+-]?[\d\.]+)%\s*,\s*([+-]?[\d\.]+)%\s*(?:,\s*([+-]?[\d\.]+)\s*)?\)/;
   varmatch=string.match(hsl);
   if(match){
      varalpha=parseFloat(match[4]);
      varh=scale(parseInt(match[1]),0,360),
          s=scale(parseFloat(match[2]),0,100),
          l=scale(parseFloat(match[3]),0,100),
          a=scale(isNaN(alpha)?1:alpha,0,1);
      return[h,s,l,a];
   }
}

functiongetHwb(string){
   if(!string){
      return;
   }
   varhwb=/^hwb\(\s*([+-]?\d+)(?:deg)?\s*,\s*([+-]?[\d\.]+)%\s*,\s*([+-]?[\d\.]+)%\s*(?:,\s*([+-]?[\d\.]+)\s*)?\)/;
   varmatch=string.match(hwb);
   if(match){
    varalpha=parseFloat(match[4]);
      varh=scale(parseInt(match[1]),0,360),
          w=scale(parseFloat(match[2]),0,100),
          b=scale(parseFloat(match[3]),0,100),
          a=scale(isNaN(alpha)?1:alpha,0,1);
      return[h,w,b,a];
   }
}

functiongetRgb(string){
   varrgba=getRgba(string);
   returnrgba&&rgba.slice(0,3);
}

functiongetHsl(string){
  varhsla=getHsla(string);
  returnhsla&&hsla.slice(0,3);
}

functiongetAlpha(string){
   varvals=getRgba(string);
   if(vals){
      returnvals[3];
   }
   elseif(vals=getHsla(string)){
      returnvals[3];
   }
   elseif(vals=getHwb(string)){
      returnvals[3];
   }
}

//generators
functionhexString(rgba,a){
   vara=(a!==undefined&&rgba.length===3)?a:rgba[3];
   return"#"+hexDouble(rgba[0])
              +hexDouble(rgba[1])
              +hexDouble(rgba[2])
              +(
                 (a>=0&&a<1)
                 ?hexDouble(Math.round(a*255))
                 :""
              );
}

functionrgbString(rgba,alpha){
   if(alpha<1||(rgba[3]&&rgba[3]<1)){
      returnrgbaString(rgba,alpha);
   }
   return"rgb("+rgba[0]+","+rgba[1]+","+rgba[2]+")";
}

functionrgbaString(rgba,alpha){
   if(alpha===undefined){
      alpha=(rgba[3]!==undefined?rgba[3]:1);
   }
   return"rgba("+rgba[0]+","+rgba[1]+","+rgba[2]
           +","+alpha+")";
}

functionpercentString(rgba,alpha){
   if(alpha<1||(rgba[3]&&rgba[3]<1)){
      returnpercentaString(rgba,alpha);
   }
   varr=Math.round(rgba[0]/255*100),
       g=Math.round(rgba[1]/255*100),
       b=Math.round(rgba[2]/255*100);

   return"rgb("+r+"%,"+g+"%,"+b+"%)";
}

functionpercentaString(rgba,alpha){
   varr=Math.round(rgba[0]/255*100),
       g=Math.round(rgba[1]/255*100),
       b=Math.round(rgba[2]/255*100);
   return"rgba("+r+"%,"+g+"%,"+b+"%,"+(alpha||rgba[3]||1)+")";
}

functionhslString(hsla,alpha){
   if(alpha<1||(hsla[3]&&hsla[3]<1)){
      returnhslaString(hsla,alpha);
   }
   return"hsl("+hsla[0]+","+hsla[1]+"%,"+hsla[2]+"%)";
}

functionhslaString(hsla,alpha){
   if(alpha===undefined){
      alpha=(hsla[3]!==undefined?hsla[3]:1);
   }
   return"hsla("+hsla[0]+","+hsla[1]+"%,"+hsla[2]+"%,"
           +alpha+")";
}

//hwbisabitdifferentthanrgb(a)&hsl(a)sincethereisnoalphaspecificsyntax
//(hwbhavealphaoptional&1isdefaultvalue)
functionhwbString(hwb,alpha){
   if(alpha===undefined){
      alpha=(hwb[3]!==undefined?hwb[3]:1);
   }
   return"hwb("+hwb[0]+","+hwb[1]+"%,"+hwb[2]+"%"
           +(alpha!==undefined&&alpha!==1?","+alpha:"")+")";
}

functionkeyword(rgb){
  returnreverseNames[rgb.slice(0,3)];
}

//helpers
functionscale(num,min,max){
   returnMath.min(Math.max(min,num),max);
}

functionhexDouble(num){
  varstr=num.toString(16).toUpperCase();
  return(str.length<2)?"0"+str:str;
}


//createalistofreversecolornames
varreverseNames={};
for(varnameincolorName$1){
   reverseNames[colorName$1[name]]=name;
}

/*MITlicense*/



varColor=function(obj){
	if(objinstanceofColor){
		returnobj;
	}
	if(!(thisinstanceofColor)){
		returnnewColor(obj);
	}

	this.valid=false;
	this.values={
		rgb:[0,0,0],
		hsl:[0,0,0],
		hsv:[0,0,0],
		hwb:[0,0,0],
		cmyk:[0,0,0,0],
		alpha:1
	};

	//parseColor()argument
	varvals;
	if(typeofobj==='string'){
		vals=colorString.getRgba(obj);
		if(vals){
			this.setValues('rgb',vals);
		}elseif(vals=colorString.getHsla(obj)){
			this.setValues('hsl',vals);
		}elseif(vals=colorString.getHwb(obj)){
			this.setValues('hwb',vals);
		}
	}elseif(typeofobj==='object'){
		vals=obj;
		if(vals.r!==undefined||vals.red!==undefined){
			this.setValues('rgb',vals);
		}elseif(vals.l!==undefined||vals.lightness!==undefined){
			this.setValues('hsl',vals);
		}elseif(vals.v!==undefined||vals.value!==undefined){
			this.setValues('hsv',vals);
		}elseif(vals.w!==undefined||vals.whiteness!==undefined){
			this.setValues('hwb',vals);
		}elseif(vals.c!==undefined||vals.cyan!==undefined){
			this.setValues('cmyk',vals);
		}
	}
};

Color.prototype={
	isValid:function(){
		returnthis.valid;
	},
	rgb:function(){
		returnthis.setSpace('rgb',arguments);
	},
	hsl:function(){
		returnthis.setSpace('hsl',arguments);
	},
	hsv:function(){
		returnthis.setSpace('hsv',arguments);
	},
	hwb:function(){
		returnthis.setSpace('hwb',arguments);
	},
	cmyk:function(){
		returnthis.setSpace('cmyk',arguments);
	},

	rgbArray:function(){
		returnthis.values.rgb;
	},
	hslArray:function(){
		returnthis.values.hsl;
	},
	hsvArray:function(){
		returnthis.values.hsv;
	},
	hwbArray:function(){
		varvalues=this.values;
		if(values.alpha!==1){
			returnvalues.hwb.concat([values.alpha]);
		}
		returnvalues.hwb;
	},
	cmykArray:function(){
		returnthis.values.cmyk;
	},
	rgbaArray:function(){
		varvalues=this.values;
		returnvalues.rgb.concat([values.alpha]);
	},
	hslaArray:function(){
		varvalues=this.values;
		returnvalues.hsl.concat([values.alpha]);
	},
	alpha:function(val){
		if(val===undefined){
			returnthis.values.alpha;
		}
		this.setValues('alpha',val);
		returnthis;
	},

	red:function(val){
		returnthis.setChannel('rgb',0,val);
	},
	green:function(val){
		returnthis.setChannel('rgb',1,val);
	},
	blue:function(val){
		returnthis.setChannel('rgb',2,val);
	},
	hue:function(val){
		if(val){
			val%=360;
			val=val<0?360+val:val;
		}
		returnthis.setChannel('hsl',0,val);
	},
	saturation:function(val){
		returnthis.setChannel('hsl',1,val);
	},
	lightness:function(val){
		returnthis.setChannel('hsl',2,val);
	},
	saturationv:function(val){
		returnthis.setChannel('hsv',1,val);
	},
	whiteness:function(val){
		returnthis.setChannel('hwb',1,val);
	},
	blackness:function(val){
		returnthis.setChannel('hwb',2,val);
	},
	value:function(val){
		returnthis.setChannel('hsv',2,val);
	},
	cyan:function(val){
		returnthis.setChannel('cmyk',0,val);
	},
	magenta:function(val){
		returnthis.setChannel('cmyk',1,val);
	},
	yellow:function(val){
		returnthis.setChannel('cmyk',2,val);
	},
	black:function(val){
		returnthis.setChannel('cmyk',3,val);
	},

	hexString:function(){
		returncolorString.hexString(this.values.rgb);
	},
	rgbString:function(){
		returncolorString.rgbString(this.values.rgb,this.values.alpha);
	},
	rgbaString:function(){
		returncolorString.rgbaString(this.values.rgb,this.values.alpha);
	},
	percentString:function(){
		returncolorString.percentString(this.values.rgb,this.values.alpha);
	},
	hslString:function(){
		returncolorString.hslString(this.values.hsl,this.values.alpha);
	},
	hslaString:function(){
		returncolorString.hslaString(this.values.hsl,this.values.alpha);
	},
	hwbString:function(){
		returncolorString.hwbString(this.values.hwb,this.values.alpha);
	},
	keyword:function(){
		returncolorString.keyword(this.values.rgb,this.values.alpha);
	},

	rgbNumber:function(){
		varrgb=this.values.rgb;
		return(rgb[0]<<16)|(rgb[1]<<8)|rgb[2];
	},

	luminosity:function(){
		//http://www.w3.org/TR/WCAG20/#relativeluminancedef
		varrgb=this.values.rgb;
		varlum=[];
		for(vari=0;i<rgb.length;i++){
			varchan=rgb[i]/255;
			lum[i]=(chan<=0.03928)?chan/12.92:Math.pow(((chan+0.055)/1.055),2.4);
		}
		return0.2126*lum[0]+0.7152*lum[1]+0.0722*lum[2];
	},

	contrast:function(color2){
		//http://www.w3.org/TR/WCAG20/#contrast-ratiodef
		varlum1=this.luminosity();
		varlum2=color2.luminosity();
		if(lum1>lum2){
			return(lum1+0.05)/(lum2+0.05);
		}
		return(lum2+0.05)/(lum1+0.05);
	},

	level:function(color2){
		varcontrastRatio=this.contrast(color2);
		if(contrastRatio>=7.1){
			return'AAA';
		}

		return(contrastRatio>=4.5)?'AA':'';
	},

	dark:function(){
		//YIQequationfromhttp://24ways.org/2010/calculating-color-contrast
		varrgb=this.values.rgb;
		varyiq=(rgb[0]*299+rgb[1]*587+rgb[2]*114)/1000;
		returnyiq<128;
	},

	light:function(){
		return!this.dark();
	},

	negate:function(){
		varrgb=[];
		for(vari=0;i<3;i++){
			rgb[i]=255-this.values.rgb[i];
		}
		this.setValues('rgb',rgb);
		returnthis;
	},

	lighten:function(ratio){
		varhsl=this.values.hsl;
		hsl[2]+=hsl[2]*ratio;
		this.setValues('hsl',hsl);
		returnthis;
	},

	darken:function(ratio){
		varhsl=this.values.hsl;
		hsl[2]-=hsl[2]*ratio;
		this.setValues('hsl',hsl);
		returnthis;
	},

	saturate:function(ratio){
		varhsl=this.values.hsl;
		hsl[1]+=hsl[1]*ratio;
		this.setValues('hsl',hsl);
		returnthis;
	},

	desaturate:function(ratio){
		varhsl=this.values.hsl;
		hsl[1]-=hsl[1]*ratio;
		this.setValues('hsl',hsl);
		returnthis;
	},

	whiten:function(ratio){
		varhwb=this.values.hwb;
		hwb[1]+=hwb[1]*ratio;
		this.setValues('hwb',hwb);
		returnthis;
	},

	blacken:function(ratio){
		varhwb=this.values.hwb;
		hwb[2]+=hwb[2]*ratio;
		this.setValues('hwb',hwb);
		returnthis;
	},

	greyscale:function(){
		varrgb=this.values.rgb;
		//http://en.wikipedia.org/wiki/Grayscale#Converting_color_to_grayscale
		varval=rgb[0]*0.3+rgb[1]*0.59+rgb[2]*0.11;
		this.setValues('rgb',[val,val,val]);
		returnthis;
	},

	clearer:function(ratio){
		varalpha=this.values.alpha;
		this.setValues('alpha',alpha-(alpha*ratio));
		returnthis;
	},

	opaquer:function(ratio){
		varalpha=this.values.alpha;
		this.setValues('alpha',alpha+(alpha*ratio));
		returnthis;
	},

	rotate:function(degrees){
		varhsl=this.values.hsl;
		varhue=(hsl[0]+degrees)%360;
		hsl[0]=hue<0?360+hue:hue;
		this.setValues('hsl',hsl);
		returnthis;
	},

	/**
	*PortedfromsassimplementationinC
	*https://github.com/sass/libsass/blob/0e6b4a2850092356aa3ece07c6b249f0221caced/functions.cpp#L209
	*/
	mix:function(mixinColor,weight){
		varcolor1=this;
		varcolor2=mixinColor;
		varp=weight===undefined?0.5:weight;

		varw=2*p-1;
		vara=color1.alpha()-color2.alpha();

		varw1=(((w*a===-1)?w:(w+a)/(1+w*a))+1)/2.0;
		varw2=1-w1;

		returnthis
			.rgb(
				w1*color1.red()+w2*color2.red(),
				w1*color1.green()+w2*color2.green(),
				w1*color1.blue()+w2*color2.blue()
			)
			.alpha(color1.alpha()*p+color2.alpha()*(1-p));
	},

	toJSON:function(){
		returnthis.rgb();
	},

	clone:function(){
		//NOTE(SB):usingnode-clonecreatesadependencytoBufferwhenusingbrowserify,
		//makingthefinalbuildwaytobigtoembedinChart.js.Solet'sdoitmanually,
		//assumingthatvaluestocloneare1dimensionarrayscontainingonlynumbers,
		//except'alpha'whichisanumber.
		varresult=newColor();
		varsource=this.values;
		vartarget=result.values;
		varvalue,type;

		for(varpropinsource){
			if(source.hasOwnProperty(prop)){
				value=source[prop];
				type=({}).toString.call(value);
				if(type==='[objectArray]'){
					target[prop]=value.slice(0);
				}elseif(type==='[objectNumber]'){
					target[prop]=value;
				}else{
					console.error('unexpectedcolorvalue:',value);
				}
			}
		}

		returnresult;
	}
};

Color.prototype.spaces={
	rgb:['red','green','blue'],
	hsl:['hue','saturation','lightness'],
	hsv:['hue','saturation','value'],
	hwb:['hue','whiteness','blackness'],
	cmyk:['cyan','magenta','yellow','black']
};

Color.prototype.maxes={
	rgb:[255,255,255],
	hsl:[360,100,100],
	hsv:[360,100,100],
	hwb:[360,100,100],
	cmyk:[100,100,100,100]
};

Color.prototype.getValues=function(space){
	varvalues=this.values;
	varvals={};

	for(vari=0;i<space.length;i++){
		vals[space.charAt(i)]=values[space][i];
	}

	if(values.alpha!==1){
		vals.a=values.alpha;
	}

	//{r:255,g:255,b:255,a:0.4}
	returnvals;
};

Color.prototype.setValues=function(space,vals){
	varvalues=this.values;
	varspaces=this.spaces;
	varmaxes=this.maxes;
	varalpha=1;
	vari;

	this.valid=true;

	if(space==='alpha'){
		alpha=vals;
	}elseif(vals.length){
		//[10,10,10]
		values[space]=vals.slice(0,space.length);
		alpha=vals[space.length];
	}elseif(vals[space.charAt(0)]!==undefined){
		//{r:10,g:10,b:10}
		for(i=0;i<space.length;i++){
			values[space][i]=vals[space.charAt(i)];
		}

		alpha=vals.a;
	}elseif(vals[spaces[space][0]]!==undefined){
		//{red:10,green:10,blue:10}
		varchans=spaces[space];

		for(i=0;i<space.length;i++){
			values[space][i]=vals[chans[i]];
		}

		alpha=vals.alpha;
	}

	values.alpha=Math.max(0,Math.min(1,(alpha===undefined?values.alpha:alpha)));

	if(space==='alpha'){
		returnfalse;
	}

	varcapped;

	//capvaluesofthespacepriorconvertingallvalues
	for(i=0;i<space.length;i++){
		capped=Math.max(0,Math.min(maxes[space][i],values[space][i]));
		values[space][i]=Math.round(capped);
	}

	//converttoalltheothercolorspaces
	for(varsnameinspaces){
		if(sname!==space){
			values[sname]=colorConvert[space][sname](values[space]);
		}
	}

	returntrue;
};

Color.prototype.setSpace=function(space,args){
	varvals=args[0];

	if(vals===undefined){
		//color.rgb()
		returnthis.getValues(space);
	}

	//color.rgb(10,10,10)
	if(typeofvals==='number'){
		vals=Array.prototype.slice.call(args);
	}

	this.setValues(space,vals);
	returnthis;
};

Color.prototype.setChannel=function(space,index,val){
	varsvalues=this.values[space];
	if(val===undefined){
		//color.red()
		returnsvalues[index];
	}elseif(val===svalues[index]){
		//color.red(color.red())
		returnthis;
	}

	//color.red(100)
	svalues[index]=val;
	this.setValues(space,svalues);

	returnthis;
};

if(typeofwindow!=='undefined'){
	window.Color=Color;
}

varchartjsColor=Color;

functionisValidKey(key){
	return['__proto__','prototype','constructor'].indexOf(key)===-1;
}

/**
 *@namespaceChart.helpers
 */
varhelpers={
	/**
	*Anemptyfunctionthatcanbeused,forexample,foroptionalcallback.
	*/
	noop:function(){},

	/**
	*Returnsauniqueid,sequentiallygeneratedfromaglobalvariable.
	*@returns{number}
	*@function
	*/
	uid:(function(){
		varid=0;
		returnfunction(){
			returnid++;
		};
	}()),

	/**
	*Returnstrueif`value`isneithernullnorundefined,elsereturnsfalse.
	*@param{*}value-Thevaluetotest.
	*@returns{boolean}
	*@since2.7.0
	*/
	isNullOrUndef:function(value){
		returnvalue===null||typeofvalue==='undefined';
	},

	/**
	*Returnstrueif`value`isanarray(includingtypedarrays),elsereturnsfalse.
	*@param{*}value-Thevaluetotest.
	*@returns{boolean}
	*@function
	*/
	isArray:function(value){
		if(Array.isArray&&Array.isArray(value)){
			returntrue;
		}
		vartype=Object.prototype.toString.call(value);
		if(type.substr(0,7)==='[object'&&type.substr(-6)==='Array]'){
			returntrue;
		}
		returnfalse;
	},

	/**
	*Returnstrueif`value`isanobject(excludingnull),elsereturnsfalse.
	*@param{*}value-Thevaluetotest.
	*@returns{boolean}
	*@since2.7.0
	*/
	isObject:function(value){
		returnvalue!==null&&Object.prototype.toString.call(value)==='[objectObject]';
	},

	/**
	*Returnstrueif`value`isafinitenumber,elsereturnsfalse
	*@param{*}value -Thevaluetotest.
	*@returns{boolean}
	*/
	isFinite:function(value){
		return(typeofvalue==='number'||valueinstanceofNumber)&&isFinite(value);
	},

	/**
	*Returns`value`ifdefined,elsereturns`defaultValue`.
	*@param{*}value-Thevaluetoreturnifdefined.
	*@param{*}defaultValue-Thevaluetoreturnif`value`isundefined.
	*@returns{*}
	*/
	valueOrDefault:function(value,defaultValue){
		returntypeofvalue==='undefined'?defaultValue:value;
	},

	/**
	*Returnsvalueatthegiven`index`inarrayifdefined,elsereturns`defaultValue`.
	*@param{Array}value-Thearraytolookupforvalueat`index`.
	*@param{number}index-Theindexin`value`tolookupforvalue.
	*@param{*}defaultValue-Thevaluetoreturnif`value[index]`isundefined.
	*@returns{*}
	*/
	valueAtIndexOrDefault:function(value,index,defaultValue){
		returnhelpers.valueOrDefault(helpers.isArray(value)?value[index]:value,defaultValue);
	},

	/**
	*Calls`fn`withthegiven`args`inthescopedefinedby`thisArg`andreturnsthe
	*valuereturnedby`fn`.If`fn`isnotafunction,thismethodreturnsundefined.
	*@param{function}fn-Thefunctiontocall.
	*@param{Array|undefined|null}args-Theargumentswithwhich`fn`shouldbecalled.
	*@param{object}[thisArg]-Thevalueof`this`providedforthecallto`fn`.
	*@returns{*}
	*/
	callback:function(fn,args,thisArg){
		if(fn&&typeoffn.call==='function'){
			returnfn.apply(thisArg,args);
		}
	},

	/**
	*Note(SB)forperformancesake,thismethodshouldonlybeusedwhenloopabletype
	*isunknownorinnoneintensivecode(notcalledoftenandsmallloopable).Else
	*it'spreferabletousearegularfor()loopandsaveextrafunctioncalls.
	*@param{object|Array}loopable-Theobjectorarraytobeiterated.
	*@param{function}fn-Thefunctiontocallforeachitem.
	*@param{object}[thisArg]-Thevalueof`this`providedforthecallto`fn`.
	*@param{boolean}[reverse]-Iftrue,iteratesbackwardontheloopable.
	*/
	each:function(loopable,fn,thisArg,reverse){
		vari,len,keys;
		if(helpers.isArray(loopable)){
			len=loopable.length;
			if(reverse){
				for(i=len-1;i>=0;i--){
					fn.call(thisArg,loopable[i],i);
				}
			}else{
				for(i=0;i<len;i++){
					fn.call(thisArg,loopable[i],i);
				}
			}
		}elseif(helpers.isObject(loopable)){
			keys=Object.keys(loopable);
			len=keys.length;
			for(i=0;i<len;i++){
				fn.call(thisArg,loopable[keys[i]],keys[i]);
			}
		}
	},

	/**
	*Returnstrueifthe`a0`and`a1`arrayshavethesamecontent,elsereturnsfalse.
	*@seehttps://stackoverflow.com/a/14853974
	*@param{Array}a0-Thearraytocompare
	*@param{Array}a1-Thearraytocompare
	*@returns{boolean}
	*/
	arrayEquals:function(a0,a1){
		vari,ilen,v0,v1;

		if(!a0||!a1||a0.length!==a1.length){
			returnfalse;
		}

		for(i=0,ilen=a0.length;i<ilen;++i){
			v0=a0[i];
			v1=a1[i];

			if(v0instanceofArray&&v1instanceofArray){
				if(!helpers.arrayEquals(v0,v1)){
					returnfalse;
				}
			}elseif(v0!==v1){
				//NOTE:twodifferentobjectinstanceswillneverbeequal:{x:20}!={x:20}
				returnfalse;
			}
		}

		returntrue;
	},

	/**
	*Returnsadeepcopyof`source`withoutkeepingreferencesonobjectsandarrays.
	*@param{*}source-Thevaluetoclone.
	*@returns{*}
	*/
	clone:function(source){
		if(helpers.isArray(source)){
			returnsource.map(helpers.clone);
		}

		if(helpers.isObject(source)){
			vartarget=Object.create(source);
			varkeys=Object.keys(source);
			varklen=keys.length;
			vark=0;

			for(;k<klen;++k){
				target[keys[k]]=helpers.clone(source[keys[k]]);
			}

			returntarget;
		}

		returnsource;
	},

	/**
	*ThedefaultmergerwhenChart.helpers.mergeiscalledwithoutmergeroption.
	*Note(SB):alsousedbymergeConfigandmergeScaleConfigasfallback.
	*@private
	*/
	_merger:function(key,target,source,options){
		if(!isValidKey(key)){
			//Wewanttoensurewedonotcopyprototypesover
			//asthiscanpolluteglobalnamespaces
			return;
		}

		vartval=target[key];
		varsval=source[key];

		if(helpers.isObject(tval)&&helpers.isObject(sval)){
			helpers.merge(tval,sval,options);
		}else{
			target[key]=helpers.clone(sval);
		}
	},

	/**
	*Mergessource[key]intarget[key]onlyiftarget[key]isundefined.
	*@private
	*/
	_mergerIf:function(key,target,source){
		if(!isValidKey(key)){
			//Wewanttoensurewedonotcopyprototypesover
			//asthiscanpolluteglobalnamespaces
			return;
		}

		vartval=target[key];
		varsval=source[key];

		if(helpers.isObject(tval)&&helpers.isObject(sval)){
			helpers.mergeIf(tval,sval);
		}elseif(!target.hasOwnProperty(key)){
			target[key]=helpers.clone(sval);
		}
	},

	/**
	*Recursivelydeepcopies`source`propertiesinto`target`withthegiven`options`.
	*IMPORTANT:`target`isnotclonedandwillbeupdatedwith`source`properties.
	*@param{object}target-Thetargetobjectinwhichallsourcesaremergedinto.
	*@param{object|object[]}source-Object(s)tomergeinto`target`.
	*@param{object}[options]-Mergingoptions:
	*@param{function}[options.merger]-Themergemethod(key,target,source,options)
	*@returns{object}The`target`object.
	*/
	merge:function(target,source,options){
		varsources=helpers.isArray(source)?source:[source];
		varilen=sources.length;
		varmerge,i,keys,klen,k;

		if(!helpers.isObject(target)){
			returntarget;
		}

		options=options||{};
		merge=options.merger||helpers._merger;

		for(i=0;i<ilen;++i){
			source=sources[i];
			if(!helpers.isObject(source)){
				continue;
			}

			keys=Object.keys(source);
			for(k=0,klen=keys.length;k<klen;++k){
				merge(keys[k],target,source,options);
			}
		}

		returntarget;
	},

	/**
	*Recursivelydeepcopies`source`propertiesinto`target`*only*ifnotdefinedintarget.
	*IMPORTANT:`target`isnotclonedandwillbeupdatedwith`source`properties.
	*@param{object}target-Thetargetobjectinwhichallsourcesaremergedinto.
	*@param{object|object[]}source-Object(s)tomergeinto`target`.
	*@returns{object}The`target`object.
	*/
	mergeIf:function(target,source){
		returnhelpers.merge(target,source,{merger:helpers._mergerIf});
	},

	/**
	*Appliesthecontentsoftwoormoreobjectstogetherintothefirstobject.
	*@param{object}target-Thetargetobjectinwhichallobjectsaremergedinto.
	*@param{object}arg1-Objectcontainingadditionalpropertiestomergeintarget.
	*@param{object}argN-Additionalobjectscontainingpropertiestomergeintarget.
	*@returns{object}The`target`object.
	*/
	extend:Object.assign||function(target){
		returnhelpers.merge(target,[].slice.call(arguments,1),{
			merger:function(key,dst,src){
				dst[key]=src[key];
			}
		});
	},

	/**
	*BasicjavascriptinheritancebasedonthemodelcreatedinBackbone.js
	*/
	inherits:function(extensions){
		varme=this;
		varChartElement=(extensions&&extensions.hasOwnProperty('constructor'))?extensions.constructor:function(){
			returnme.apply(this,arguments);
		};

		varSurrogate=function(){
			this.constructor=ChartElement;
		};

		Surrogate.prototype=me.prototype;
		ChartElement.prototype=newSurrogate();
		ChartElement.extend=helpers.inherits;

		if(extensions){
			helpers.extend(ChartElement.prototype,extensions);
		}

		ChartElement.__super__=me.prototype;
		returnChartElement;
	},

	_deprecated:function(scope,value,previous,current){
		if(value!==undefined){
			console.warn(scope+':"'+previous+
				'"isdeprecated.Pleaseuse"'+current+'"instead');
		}
	}
};

varhelpers_core=helpers;

//DEPRECATIONS

/**
 *Providedforbackwardcompatibility,useChart.helpers.callbackinstead.
 *@functionChart.helpers.callCallback
 *@deprecatedsinceversion2.6.0
 *@todoremoveatversion3
 *@private
 */
helpers.callCallback=helpers.callback;

/**
 *Providedforbackwardcompatibility,useArray.prototype.indexOfinstead.
 *Array.prototype.indexOfcompatibility:Chrome,Opera,Safari,FF1.5+,IE9+
 *@functionChart.helpers.indexOf
 *@deprecatedsinceversion2.7.0
 *@todoremoveatversion3
 *@private
 */
helpers.indexOf=function(array,item,fromIndex){
	returnArray.prototype.indexOf.call(array,item,fromIndex);
};

/**
 *Providedforbackwardcompatibility,useChart.helpers.valueOrDefaultinstead.
 *@functionChart.helpers.getValueOrDefault
 *@deprecatedsinceversion2.7.0
 *@todoremoveatversion3
 *@private
 */
helpers.getValueOrDefault=helpers.valueOrDefault;

/**
 *Providedforbackwardcompatibility,useChart.helpers.valueAtIndexOrDefaultinstead.
 *@functionChart.helpers.getValueAtIndexOrDefault
 *@deprecatedsinceversion2.7.0
 *@todoremoveatversion3
 *@private
 */
helpers.getValueAtIndexOrDefault=helpers.valueAtIndexOrDefault;

/**
 *EasingfunctionsadaptedfromRobertPenner'seasingequations.
 *@namespaceChart.helpers.easingEffects
 *@seehttp://www.robertpenner.com/easing/
 */
vareffects={
	linear:function(t){
		returnt;
	},

	easeInQuad:function(t){
		returnt*t;
	},

	easeOutQuad:function(t){
		return-t*(t-2);
	},

	easeInOutQuad:function(t){
		if((t/=0.5)<1){
			return0.5*t*t;
		}
		return-0.5*((--t)*(t-2)-1);
	},

	easeInCubic:function(t){
		returnt*t*t;
	},

	easeOutCubic:function(t){
		return(t=t-1)*t*t+1;
	},

	easeInOutCubic:function(t){
		if((t/=0.5)<1){
			return0.5*t*t*t;
		}
		return0.5*((t-=2)*t*t+2);
	},

	easeInQuart:function(t){
		returnt*t*t*t;
	},

	easeOutQuart:function(t){
		return-((t=t-1)*t*t*t-1);
	},

	easeInOutQuart:function(t){
		if((t/=0.5)<1){
			return0.5*t*t*t*t;
		}
		return-0.5*((t-=2)*t*t*t-2);
	},

	easeInQuint:function(t){
		returnt*t*t*t*t;
	},

	easeOutQuint:function(t){
		return(t=t-1)*t*t*t*t+1;
	},

	easeInOutQuint:function(t){
		if((t/=0.5)<1){
			return0.5*t*t*t*t*t;
		}
		return0.5*((t-=2)*t*t*t*t+2);
	},

	easeInSine:function(t){
		return-Math.cos(t*(Math.PI/2))+1;
	},

	easeOutSine:function(t){
		returnMath.sin(t*(Math.PI/2));
	},

	easeInOutSine:function(t){
		return-0.5*(Math.cos(Math.PI*t)-1);
	},

	easeInExpo:function(t){
		return(t===0)?0:Math.pow(2,10*(t-1));
	},

	easeOutExpo:function(t){
		return(t===1)?1:-Math.pow(2,-10*t)+1;
	},

	easeInOutExpo:function(t){
		if(t===0){
			return0;
		}
		if(t===1){
			return1;
		}
		if((t/=0.5)<1){
			return0.5*Math.pow(2,10*(t-1));
		}
		return0.5*(-Math.pow(2,-10*--t)+2);
	},

	easeInCirc:function(t){
		if(t>=1){
			returnt;
		}
		return-(Math.sqrt(1-t*t)-1);
	},

	easeOutCirc:function(t){
		returnMath.sqrt(1-(t=t-1)*t);
	},

	easeInOutCirc:function(t){
		if((t/=0.5)<1){
			return-0.5*(Math.sqrt(1-t*t)-1);
		}
		return0.5*(Math.sqrt(1-(t-=2)*t)+1);
	},

	easeInElastic:function(t){
		vars=1.70158;
		varp=0;
		vara=1;
		if(t===0){
			return0;
		}
		if(t===1){
			return1;
		}
		if(!p){
			p=0.3;
		}
		if(a<1){
			a=1;
			s=p/4;
		}else{
			s=p/(2*Math.PI)*Math.asin(1/a);
		}
		return-(a*Math.pow(2,10*(t-=1))*Math.sin((t-s)*(2*Math.PI)/p));
	},

	easeOutElastic:function(t){
		vars=1.70158;
		varp=0;
		vara=1;
		if(t===0){
			return0;
		}
		if(t===1){
			return1;
		}
		if(!p){
			p=0.3;
		}
		if(a<1){
			a=1;
			s=p/4;
		}else{
			s=p/(2*Math.PI)*Math.asin(1/a);
		}
		returna*Math.pow(2,-10*t)*Math.sin((t-s)*(2*Math.PI)/p)+1;
	},

	easeInOutElastic:function(t){
		vars=1.70158;
		varp=0;
		vara=1;
		if(t===0){
			return0;
		}
		if((t/=0.5)===2){
			return1;
		}
		if(!p){
			p=0.45;
		}
		if(a<1){
			a=1;
			s=p/4;
		}else{
			s=p/(2*Math.PI)*Math.asin(1/a);
		}
		if(t<1){
			return-0.5*(a*Math.pow(2,10*(t-=1))*Math.sin((t-s)*(2*Math.PI)/p));
		}
		returna*Math.pow(2,-10*(t-=1))*Math.sin((t-s)*(2*Math.PI)/p)*0.5+1;
	},
	easeInBack:function(t){
		vars=1.70158;
		returnt*t*((s+1)*t-s);
	},

	easeOutBack:function(t){
		vars=1.70158;
		return(t=t-1)*t*((s+1)*t+s)+1;
	},

	easeInOutBack:function(t){
		vars=1.70158;
		if((t/=0.5)<1){
			return0.5*(t*t*(((s*=(1.525))+1)*t-s));
		}
		return0.5*((t-=2)*t*(((s*=(1.525))+1)*t+s)+2);
	},

	easeInBounce:function(t){
		return1-effects.easeOutBounce(1-t);
	},

	easeOutBounce:function(t){
		if(t<(1/2.75)){
			return7.5625*t*t;
		}
		if(t<(2/2.75)){
			return7.5625*(t-=(1.5/2.75))*t+0.75;
		}
		if(t<(2.5/2.75)){
			return7.5625*(t-=(2.25/2.75))*t+0.9375;
		}
		return7.5625*(t-=(2.625/2.75))*t+0.984375;
	},

	easeInOutBounce:function(t){
		if(t<0.5){
			returneffects.easeInBounce(t*2)*0.5;
		}
		returneffects.easeOutBounce(t*2-1)*0.5+0.5;
	}
};

varhelpers_easing={
	effects:effects
};

//DEPRECATIONS

/**
 *Providedforbackwardcompatibility,useChart.helpers.easing.effectsinstead.
 *@functionChart.helpers.easingEffects
 *@deprecatedsinceversion2.7.0
 *@todoremoveatversion3
 *@private
 */
helpers_core.easingEffects=effects;

varPI=Math.PI;
varRAD_PER_DEG=PI/180;
varDOUBLE_PI=PI*2;
varHALF_PI=PI/2;
varQUARTER_PI=PI/4;
varTWO_THIRDS_PI=PI*2/3;

/**
 *@namespaceChart.helpers.canvas
 */
varexports$1={
	/**
	*Clearstheentirecanvasassociatedtothegiven`chart`.
	*@param{Chart}chart-Thechartforwhichtoclearthecanvas.
	*/
	clear:function(chart){
		chart.ctx.clearRect(0,0,chart.width,chart.height);
	},

	/**
	*Createsa"path"forarectanglewithroundedcornersatposition(x,y)witha
	*givensize(width,height)andthesame`radius`forallcorners.
	*@param{CanvasRenderingContext2D}ctx-Thecanvas2DContext.
	*@param{number}x-Thexaxisofthecoordinatefortherectanglestartingpoint.
	*@param{number}y-Theyaxisofthecoordinatefortherectanglestartingpoint.
	*@param{number}width-Therectangle'swidth.
	*@param{number}height-Therectangle'sheight.
	*@param{number}radius-Theroundedamount(inpixels)forthefourcorners.
	*@todohandle`radius`astop-left,top-right,bottom-right,bottom-leftarray/object?
	*/
	roundedRect:function(ctx,x,y,width,height,radius){
		if(radius){
			varr=Math.min(radius,height/2,width/2);
			varleft=x+r;
			vartop=y+r;
			varright=x+width-r;
			varbottom=y+height-r;

			ctx.moveTo(x,top);
			if(left<right&&top<bottom){
				ctx.arc(left,top,r,-PI,-HALF_PI);
				ctx.arc(right,top,r,-HALF_PI,0);
				ctx.arc(right,bottom,r,0,HALF_PI);
				ctx.arc(left,bottom,r,HALF_PI,PI);
			}elseif(left<right){
				ctx.moveTo(left,y);
				ctx.arc(right,top,r,-HALF_PI,HALF_PI);
				ctx.arc(left,top,r,HALF_PI,PI+HALF_PI);
			}elseif(top<bottom){
				ctx.arc(left,top,r,-PI,0);
				ctx.arc(left,bottom,r,0,PI);
			}else{
				ctx.arc(left,top,r,-PI,PI);
			}
			ctx.closePath();
			ctx.moveTo(x,y);
		}else{
			ctx.rect(x,y,width,height);
		}
	},

	drawPoint:function(ctx,style,radius,x,y,rotation){
		vartype,xOffset,yOffset,size,cornerRadius;
		varrad=(rotation||0)*RAD_PER_DEG;

		if(style&&typeofstyle==='object'){
			type=style.toString();
			if(type==='[objectHTMLImageElement]'||type==='[objectHTMLCanvasElement]'){
				ctx.save();
				ctx.translate(x,y);
				ctx.rotate(rad);
				ctx.drawImage(style,-style.width/2,-style.height/2,style.width,style.height);
				ctx.restore();
				return;
			}
		}

		if(isNaN(radius)||radius<=0){
			return;
		}

		ctx.beginPath();

		switch(style){
		//Defaultincludescircle
		default:
			ctx.arc(x,y,radius,0,DOUBLE_PI);
			ctx.closePath();
			break;
		case'triangle':
			ctx.moveTo(x+Math.sin(rad)*radius,y-Math.cos(rad)*radius);
			rad+=TWO_THIRDS_PI;
			ctx.lineTo(x+Math.sin(rad)*radius,y-Math.cos(rad)*radius);
			rad+=TWO_THIRDS_PI;
			ctx.lineTo(x+Math.sin(rad)*radius,y-Math.cos(rad)*radius);
			ctx.closePath();
			break;
		case'rectRounded':
			//NOTE:theroundedrectimplementationchangedtouse`arc`insteadof
			//`quadraticCurveTo`sinceitgeneratesbetterresultswhenrectis
			//almostacircle.0.516(insteadof0.5)producesresultswithvisually
			//closerproportiontothepreviousimplanditisinscribedinthe
			//circlewith`radius`.Formoredetails,seethefollowingPRs:
			//https://github.com/chartjs/Chart.js/issues/5597
			//https://github.com/chartjs/Chart.js/issues/5858
			cornerRadius=radius*0.516;
			size=radius-cornerRadius;
			xOffset=Math.cos(rad+QUARTER_PI)*size;
			yOffset=Math.sin(rad+QUARTER_PI)*size;
			ctx.arc(x-xOffset,y-yOffset,cornerRadius,rad-PI,rad-HALF_PI);
			ctx.arc(x+yOffset,y-xOffset,cornerRadius,rad-HALF_PI,rad);
			ctx.arc(x+xOffset,y+yOffset,cornerRadius,rad,rad+HALF_PI);
			ctx.arc(x-yOffset,y+xOffset,cornerRadius,rad+HALF_PI,rad+PI);
			ctx.closePath();
			break;
		case'rect':
			if(!rotation){
				size=Math.SQRT1_2*radius;
				ctx.rect(x-size,y-size,2*size,2*size);
				break;
			}
			rad+=QUARTER_PI;
			/*fallsthrough*/
		case'rectRot':
			xOffset=Math.cos(rad)*radius;
			yOffset=Math.sin(rad)*radius;
			ctx.moveTo(x-xOffset,y-yOffset);
			ctx.lineTo(x+yOffset,y-xOffset);
			ctx.lineTo(x+xOffset,y+yOffset);
			ctx.lineTo(x-yOffset,y+xOffset);
			ctx.closePath();
			break;
		case'crossRot':
			rad+=QUARTER_PI;
			/*fallsthrough*/
		case'cross':
			xOffset=Math.cos(rad)*radius;
			yOffset=Math.sin(rad)*radius;
			ctx.moveTo(x-xOffset,y-yOffset);
			ctx.lineTo(x+xOffset,y+yOffset);
			ctx.moveTo(x+yOffset,y-xOffset);
			ctx.lineTo(x-yOffset,y+xOffset);
			break;
		case'star':
			xOffset=Math.cos(rad)*radius;
			yOffset=Math.sin(rad)*radius;
			ctx.moveTo(x-xOffset,y-yOffset);
			ctx.lineTo(x+xOffset,y+yOffset);
			ctx.moveTo(x+yOffset,y-xOffset);
			ctx.lineTo(x-yOffset,y+xOffset);
			rad+=QUARTER_PI;
			xOffset=Math.cos(rad)*radius;
			yOffset=Math.sin(rad)*radius;
			ctx.moveTo(x-xOffset,y-yOffset);
			ctx.lineTo(x+xOffset,y+yOffset);
			ctx.moveTo(x+yOffset,y-xOffset);
			ctx.lineTo(x-yOffset,y+xOffset);
			break;
		case'line':
			xOffset=Math.cos(rad)*radius;
			yOffset=Math.sin(rad)*radius;
			ctx.moveTo(x-xOffset,y-yOffset);
			ctx.lineTo(x+xOffset,y+yOffset);
			break;
		case'dash':
			ctx.moveTo(x,y);
			ctx.lineTo(x+Math.cos(rad)*radius,y+Math.sin(rad)*radius);
			break;
		}

		ctx.fill();
		ctx.stroke();
	},

	/**
	*Returnstrueifthepointisinsidetherectangle
	*@param{object}point-Thepointtotest
	*@param{object}area-Therectangle
	*@returns{boolean}
	*@private
	*/
	_isPointInArea:function(point,area){
		varepsilon=1e-6;//1e-6ismargininpixelsforaccumulatederror.

		returnpoint.x>area.left-epsilon&&point.x<area.right+epsilon&&
			point.y>area.top-epsilon&&point.y<area.bottom+epsilon;
	},

	clipArea:function(ctx,area){
		ctx.save();
		ctx.beginPath();
		ctx.rect(area.left,area.top,area.right-area.left,area.bottom-area.top);
		ctx.clip();
	},

	unclipArea:function(ctx){
		ctx.restore();
	},

	lineTo:function(ctx,previous,target,flip){
		varstepped=target.steppedLine;
		if(stepped){
			if(stepped==='middle'){
				varmidpoint=(previous.x+target.x)/2.0;
				ctx.lineTo(midpoint,flip?target.y:previous.y);
				ctx.lineTo(midpoint,flip?previous.y:target.y);
			}elseif((stepped==='after'&&!flip)||(stepped!=='after'&&flip)){
				ctx.lineTo(previous.x,target.y);
			}else{
				ctx.lineTo(target.x,previous.y);
			}
			ctx.lineTo(target.x,target.y);
			return;
		}

		if(!target.tension){
			ctx.lineTo(target.x,target.y);
			return;
		}

		ctx.bezierCurveTo(
			flip?previous.controlPointPreviousX:previous.controlPointNextX,
			flip?previous.controlPointPreviousY:previous.controlPointNextY,
			flip?target.controlPointNextX:target.controlPointPreviousX,
			flip?target.controlPointNextY:target.controlPointPreviousY,
			target.x,
			target.y);
	}
};

varhelpers_canvas=exports$1;

//DEPRECATIONS

/**
 *Providedforbackwardcompatibility,useChart.helpers.canvas.clearinstead.
 *@namespaceChart.helpers.clear
 *@deprecatedsinceversion2.7.0
 *@todoremoveatversion3
 *@private
 */
helpers_core.clear=exports$1.clear;

/**
 *Providedforbackwardcompatibility,useChart.helpers.canvas.roundedRectinstead.
 *@namespaceChart.helpers.drawRoundedRectangle
 *@deprecatedsinceversion2.7.0
 *@todoremoveatversion3
 *@private
 */
helpers_core.drawRoundedRectangle=function(ctx){
	ctx.beginPath();
	exports$1.roundedRect.apply(exports$1,arguments);
};

vardefaults={
	/**
	*@private
	*/
	_set:function(scope,values){
		returnhelpers_core.merge(this[scope]||(this[scope]={}),values);
	}
};

//TODO(v3):remove'global'fromnamespace. alldefaultareglobaland
//there'sinconsistencyaroundwhichoptionsareunder'global'
defaults._set('global',{
	defaultColor:'rgba(0,0,0,0.1)',
	defaultFontColor:'#666',
	defaultFontFamily:"'HelveticaNeue','Helvetica','Arial',sans-serif",
	defaultFontSize:12,
	defaultFontStyle:'normal',
	defaultLineHeight:1.2,
	showLines:true
});

varcore_defaults=defaults;

varvalueOrDefault=helpers_core.valueOrDefault;

/**
 *ConvertsthegivenfontobjectintoaCSSfontstring.
 *@param{object}font-Afontobject.
 *@return{string}TheCSSfontstring.Seehttps://developer.mozilla.org/en-US/docs/Web/CSS/font
 *@private
 */
functiontoFontString(font){
	if(!font||helpers_core.isNullOrUndef(font.size)||helpers_core.isNullOrUndef(font.family)){
		returnnull;
	}

	return(font.style?font.style+'':'')
		+(font.weight?font.weight+'':'')
		+font.size+'px'
		+font.family;
}

/**
 *@aliasChart.helpers.options
 *@namespace
 */
varhelpers_options={
	/**
	*Convertsthegivenlineheight`value`inpixelsforaspecificfont`size`.
	*@param{number|string}value-ThelineHeighttoparse(eg.1.6,'14px','75%','1.6em').
	*@param{number}size-Thefontsize(inpixels)usedtoresolverelative`value`.
	*@returns{number}Theeffectivelineheightinpixels(size*1.2ifvalueisinvalid).
	*@seehttps://developer.mozilla.org/en-US/docs/Web/CSS/line-height
	*@since2.7.0
	*/
	toLineHeight:function(value,size){
		varmatches=(''+value).match(/^(normal|(\d+(?:\.\d+)?)(px|em|%)?)$/);
		if(!matches||matches[1]==='normal'){
			returnsize*1.2;
		}

		value=+matches[2];

		switch(matches[3]){
		case'px':
			returnvalue;
		case'%':
			value/=100;
			break;
		}

		returnsize*value;
	},

	/**
	*Convertsthegivenvalueintoapaddingobjectwithpre-computedwidth/height.
	*@param{number|object}value-Ifanumber,setthevaluetoallTRBLcomponent,
	* else,ifandobject,usedefinedpropertiesandsetsundefinedonesto0.
	*@returns{object}Thepaddingvalues(top,right,bottom,left,width,height)
	*@since2.7.0
	*/
	toPadding:function(value){
		vart,r,b,l;

		if(helpers_core.isObject(value)){
			t=+value.top||0;
			r=+value.right||0;
			b=+value.bottom||0;
			l=+value.left||0;
		}else{
			t=r=b=l=+value||0;
		}

		return{
			top:t,
			right:r,
			bottom:b,
			left:l,
			height:t+b,
			width:l+r
		};
	},

	/**
	*Parsesfontoptionsandreturnsthefontobject.
	*@param{object}options-Aobjectthatcontainsfontoptionstobeparsed.
	*@return{object}Thefontobject.
	*@todoSupportfont.*optionsandrenamedtotoFont().
	*@private
	*/
	_parseFont:function(options){
		varglobalDefaults=core_defaults.global;
		varsize=valueOrDefault(options.fontSize,globalDefaults.defaultFontSize);
		varfont={
			family:valueOrDefault(options.fontFamily,globalDefaults.defaultFontFamily),
			lineHeight:helpers_core.options.toLineHeight(valueOrDefault(options.lineHeight,globalDefaults.defaultLineHeight),size),
			size:size,
			style:valueOrDefault(options.fontStyle,globalDefaults.defaultFontStyle),
			weight:null,
			string:''
		};

		font.string=toFontString(font);
		returnfont;
	},

	/**
	*Evaluatesthegiven`inputs`sequentiallyandreturnsthefirstdefinedvalue.
	*@param{Array}inputs-Anarrayofvalues,fallingbacktothelastvalue.
	*@param{object}[context]-Ifdefinedandthecurrentvalueisafunction,thevalue
	*iscalledwith`context`asfirstargumentandtheresultbecomesthenewinput.
	*@param{number}[index]-Ifdefinedandthecurrentvalueisanarray,thevalue
	*at`index`becomethenewinput.
	*@param{object}[info]-objecttoreturninformationaboutresolutionin
	*@param{boolean}[info.cacheable]-Willbesetto`false`ifoptionisnotcacheable.
	*@since2.7.0
	*/
	resolve:function(inputs,context,index,info){
		varcacheable=true;
		vari,ilen,value;

		for(i=0,ilen=inputs.length;i<ilen;++i){
			value=inputs[i];
			if(value===undefined){
				continue;
			}
			if(context!==undefined&&typeofvalue==='function'){
				value=value(context);
				cacheable=false;
			}
			if(index!==undefined&&helpers_core.isArray(value)){
				value=value[index];
				cacheable=false;
			}
			if(value!==undefined){
				if(info&&!cacheable){
					info.cacheable=false;
				}
				returnvalue;
			}
		}
	}
};

/**
 *@aliasChart.helpers.math
 *@namespace
 */
varexports$2={
	/**
	*Returnsanarrayoffactorssortedfrom1tosqrt(value)
	*@private
	*/
	_factorize:function(value){
		varresult=[];
		varsqrt=Math.sqrt(value);
		vari;

		for(i=1;i<sqrt;i++){
			if(value%i===0){
				result.push(i);
				result.push(value/i);
			}
		}
		if(sqrt===(sqrt|0)){//ifvalueisasquarenumber
			result.push(sqrt);
		}

		result.sort(function(a,b){
			returna-b;
		}).pop();
		returnresult;
	},

	log10:Math.log10||function(x){
		varexponent=Math.log(x)*Math.LOG10E;//Math.LOG10E=1/Math.LN10.
		//Checkforwholepowersof10,
		//whichduetofloatingpointroundingerrorshouldbecorrected.
		varpowerOf10=Math.round(exponent);
		varisPowerOf10=x===Math.pow(10,powerOf10);

		returnisPowerOf10?powerOf10:exponent;
	}
};

varhelpers_math=exports$2;

//DEPRECATIONS

/**
 *Providedforbackwardcompatibility,useChart.helpers.math.log10instead.
 *@namespaceChart.helpers.log10
 *@deprecatedsinceversion2.9.0
 *@todoremoveatversion3
 *@private
 */
helpers_core.log10=exports$2.log10;

vargetRtlAdapter=function(rectX,width){
	return{
		x:function(x){
			returnrectX+rectX+width-x;
		},
		setWidth:function(w){
			width=w;
		},
		textAlign:function(align){
			if(align==='center'){
				returnalign;
			}
			returnalign==='right'?'left':'right';
		},
		xPlus:function(x,value){
			returnx-value;
		},
		leftForLtr:function(x,itemWidth){
			returnx-itemWidth;
		},
	};
};

vargetLtrAdapter=function(){
	return{
		x:function(x){
			returnx;
		},
		setWidth:function(w){//eslint-disable-lineno-unused-vars
		},
		textAlign:function(align){
			returnalign;
		},
		xPlus:function(x,value){
			returnx+value;
		},
		leftForLtr:function(x,_itemWidth){//eslint-disable-lineno-unused-vars
			returnx;
		},
	};
};

vargetAdapter=function(rtl,rectX,width){
	returnrtl?getRtlAdapter(rectX,width):getLtrAdapter();
};

varoverrideTextDirection=function(ctx,direction){
	varstyle,original;
	if(direction==='ltr'||direction==='rtl'){
		style=ctx.canvas.style;
		original=[
			style.getPropertyValue('direction'),
			style.getPropertyPriority('direction'),
		];

		style.setProperty('direction',direction,'important');
		ctx.prevTextDirection=original;
	}
};

varrestoreTextDirection=function(ctx){
	varoriginal=ctx.prevTextDirection;
	if(original!==undefined){
		deletectx.prevTextDirection;
		ctx.canvas.style.setProperty('direction',original[0],original[1]);
	}
};

varhelpers_rtl={
	getRtlAdapter:getAdapter,
	overrideTextDirection:overrideTextDirection,
	restoreTextDirection:restoreTextDirection,
};

varhelpers$1=helpers_core;
vareasing=helpers_easing;
varcanvas=helpers_canvas;
varoptions=helpers_options;
varmath=helpers_math;
varrtl=helpers_rtl;
helpers$1.easing=easing;
helpers$1.canvas=canvas;
helpers$1.options=options;
helpers$1.math=math;
helpers$1.rtl=rtl;

functioninterpolate(start,view,model,ease){
	varkeys=Object.keys(model);
	vari,ilen,key,actual,origin,target,type,c0,c1;

	for(i=0,ilen=keys.length;i<ilen;++i){
		key=keys[i];

		target=model[key];

		//ifavalueisaddedtothemodelafterpivot()hasbeencalled,theview
		//doesn'tcontainit,solet'sinitializetheviewtothetargetvalue.
		if(!view.hasOwnProperty(key)){
			view[key]=target;
		}

		actual=view[key];

		if(actual===target||key[0]==='_'){
			continue;
		}

		if(!start.hasOwnProperty(key)){
			start[key]=actual;
		}

		origin=start[key];

		type=typeoftarget;

		if(type===typeoforigin){
			if(type==='string'){
				c0=chartjsColor(origin);
				if(c0.valid){
					c1=chartjsColor(target);
					if(c1.valid){
						view[key]=c1.mix(c0,ease).rgbString();
						continue;
					}
				}
			}elseif(helpers$1.isFinite(origin)&&helpers$1.isFinite(target)){
				view[key]=origin+(target-origin)*ease;
				continue;
			}
		}

		view[key]=target;
	}
}

varElement=function(configuration){
	helpers$1.extend(this,configuration);
	this.initialize.apply(this,arguments);
};

helpers$1.extend(Element.prototype,{
	_type:undefined,

	initialize:function(){
		this.hidden=false;
	},

	pivot:function(){
		varme=this;
		if(!me._view){
			me._view=helpers$1.extend({},me._model);
		}
		me._start={};
		returnme;
	},

	transition:function(ease){
		varme=this;
		varmodel=me._model;
		varstart=me._start;
		varview=me._view;

		//Noanimation->NoTransition
		if(!model||ease===1){
			me._view=helpers$1.extend({},model);
			me._start=null;
			returnme;
		}

		if(!view){
			view=me._view={};
		}

		if(!start){
			start=me._start={};
		}

		interpolate(start,view,model,ease);

		returnme;
	},

	tooltipPosition:function(){
		return{
			x:this._model.x,
			y:this._model.y
		};
	},

	hasValue:function(){
		returnhelpers$1.isNumber(this._model.x)&&helpers$1.isNumber(this._model.y);
	}
});

Element.extend=helpers$1.inherits;

varcore_element=Element;

varexports$3=core_element.extend({
	chart:null,//theanimationassociatedchartinstance
	currentStep:0,//thecurrentanimationstep
	numSteps:60,//defaultnumberofsteps
	easing:'',//theeasingtouseforthisanimation
	render:null,//renderfunctionusedbytheanimationservice

	onAnimationProgress:null,//userspecifiedcallbacktofireoneachstepoftheanimation
	onAnimationComplete:null,//userspecifiedcallbacktofirewhentheanimationfinishes
});

varcore_animation=exports$3;

//DEPRECATIONS

/**
 *Providedforbackwardcompatibility,useChart.Animationinstead
 *@propChart.Animation#animationObject
 *@deprecatedsinceversion2.6.0
 *@todoremoveatversion3
 */
Object.defineProperty(exports$3.prototype,'animationObject',{
	get:function(){
		returnthis;
	}
});

/**
 *Providedforbackwardcompatibility,useChart.Animation#chartinstead
 *@propChart.Animation#chartInstance
 *@deprecatedsinceversion2.6.0
 *@todoremoveatversion3
 */
Object.defineProperty(exports$3.prototype,'chartInstance',{
	get:function(){
		returnthis.chart;
	},
	set:function(value){
		this.chart=value;
	}
});

core_defaults._set('global',{
	animation:{
		duration:1000,
		easing:'easeOutQuart',
		onProgress:helpers$1.noop,
		onComplete:helpers$1.noop
	}
});

varcore_animations={
	animations:[],
	request:null,

	/**
	*@param{Chart}chart-Thecharttoanimate.
	*@param{Chart.Animation}animation-Theanimationthatwewillanimate.
	*@param{number}duration-Theanimationdurationinms.
	*@param{boolean}lazy-iftrue,thechartisnotmarkedasanimatingtoenablemoreresponsiveinteractions
	*/
	addAnimation:function(chart,animation,duration,lazy){
		varanimations=this.animations;
		vari,ilen;

		animation.chart=chart;
		animation.startTime=Date.now();
		animation.duration=duration;

		if(!lazy){
			chart.animating=true;
		}

		for(i=0,ilen=animations.length;i<ilen;++i){
			if(animations[i].chart===chart){
				animations[i]=animation;
				return;
			}
		}

		animations.push(animation);

		//Iftherearenoanimationsqueued,manuallykickstartadigest,forlackofabetterword
		if(animations.length===1){
			this.requestAnimationFrame();
		}
	},

	cancelAnimation:function(chart){
		varindex=helpers$1.findIndex(this.animations,function(animation){
			returnanimation.chart===chart;
		});

		if(index!==-1){
			this.animations.splice(index,1);
			chart.animating=false;
		}
	},

	requestAnimationFrame:function(){
		varme=this;
		if(me.request===null){
			//Skipanimationframerequestsuntiltheactiveoneisexecuted.
			//Thiscanhappenwhenprocessingmouseevents,e.g.'mousemove'
			//and'mouseout'eventswilltriggermultiplerenders.
			me.request=helpers$1.requestAnimFrame.call(window,function(){
				me.request=null;
				me.startDigest();
			});
		}
	},

	/**
	*@private
	*/
	startDigest:function(){
		varme=this;

		me.advance();

		//Dowehavemorestufftoanimate?
		if(me.animations.length>0){
			me.requestAnimationFrame();
		}
	},

	/**
	*@private
	*/
	advance:function(){
		varanimations=this.animations;
		varanimation,chart,numSteps,nextStep;
		vari=0;

		//1animationperchart,soweareloopingchartshere
		while(i<animations.length){
			animation=animations[i];
			chart=animation.chart;
			numSteps=animation.numSteps;

			//MakesurethatcurrentStepstartsat1
			//https://github.com/chartjs/Chart.js/issues/6104
			nextStep=Math.floor((Date.now()-animation.startTime)/animation.duration*numSteps)+1;
			animation.currentStep=Math.min(nextStep,numSteps);

			helpers$1.callback(animation.render,[chart,animation],chart);
			helpers$1.callback(animation.onAnimationProgress,[animation],chart);

			if(animation.currentStep>=numSteps){
				helpers$1.callback(animation.onAnimationComplete,[animation],chart);
				chart.animating=false;
				animations.splice(i,1);
			}else{
				++i;
			}
		}
	}
};

varresolve=helpers$1.options.resolve;

vararrayEvents=['push','pop','shift','splice','unshift'];

/**
 *Hooksthearraymethodsthataddorremovevalues('push',pop','shift','splice',
 *'unshift')andnotifythelistenerAFTERthearrayhasbeenaltered.Listenersare
 *calledonthe'onData*'callbacks(e.g.onDataPush,etc.)withsamearguments.
 */
functionlistenArrayEvents(array,listener){
	if(array._chartjs){
		array._chartjs.listeners.push(listener);
		return;
	}

	Object.defineProperty(array,'_chartjs',{
		configurable:true,
		enumerable:false,
		value:{
			listeners:[listener]
		}
	});

	arrayEvents.forEach(function(key){
		varmethod='onData'+key.charAt(0).toUpperCase()+key.slice(1);
		varbase=array[key];

		Object.defineProperty(array,key,{
			configurable:true,
			enumerable:false,
			value:function(){
				varargs=Array.prototype.slice.call(arguments);
				varres=base.apply(this,args);

				helpers$1.each(array._chartjs.listeners,function(object){
					if(typeofobject[method]==='function'){
						object[method].apply(object,args);
					}
				});

				returnres;
			}
		});
	});
}

/**
 *Removesthegivenarrayeventlistenerandcleanupextraattachedproperties(suchas
 *the_chartjsstubandoverriddenmethods)ifarraydoesn'thaveanymorelisteners.
 */
functionunlistenArrayEvents(array,listener){
	varstub=array._chartjs;
	if(!stub){
		return;
	}

	varlisteners=stub.listeners;
	varindex=listeners.indexOf(listener);
	if(index!==-1){
		listeners.splice(index,1);
	}

	if(listeners.length>0){
		return;
	}

	arrayEvents.forEach(function(key){
		deletearray[key];
	});

	deletearray._chartjs;
}

//Baseclassforalldatasetcontrollers(line,bar,etc)
varDatasetController=function(chart,datasetIndex){
	this.initialize(chart,datasetIndex);
};

helpers$1.extend(DatasetController.prototype,{

	/**
	*Elementtypeusedtogenerateametadataset(e.g.Chart.element.Line).
	*@type{Chart.core.element}
	*/
	datasetElementType:null,

	/**
	*Elementtypeusedtogenerateametadata(e.g.Chart.element.Point).
	*@type{Chart.core.element}
	*/
	dataElementType:null,

	/**
	*Datasetelementoptionkeystoberesolvedin_resolveDatasetElementOptions.
	*Aderivedcontrollermayoverridethistoresolvecontroller-specificoptions.
	*Thekeysdefinedhereareforbackwardcompatibilityforlegendstyles.
	*@private
	*/
	_datasetElementOptions:[
		'backgroundColor',
		'borderCapStyle',
		'borderColor',
		'borderDash',
		'borderDashOffset',
		'borderJoinStyle',
		'borderWidth'
	],

	/**
	*Dataelementoptionkeystoberesolvedin_resolveDataElementOptions.
	*Aderivedcontrollermayoverridethistoresolvecontroller-specificoptions.
	*Thekeysdefinedhereareforbackwardcompatibilityforlegendstyles.
	*@private
	*/
	_dataElementOptions:[
		'backgroundColor',
		'borderColor',
		'borderWidth',
		'pointStyle'
	],

	initialize:function(chart,datasetIndex){
		varme=this;
		me.chart=chart;
		me.index=datasetIndex;
		me.linkScales();
		me.addElements();
		me._type=me.getMeta().type;
	},

	updateIndex:function(datasetIndex){
		this.index=datasetIndex;
	},

	linkScales:function(){
		varme=this;
		varmeta=me.getMeta();
		varchart=me.chart;
		varscales=chart.scales;
		vardataset=me.getDataset();
		varscalesOpts=chart.options.scales;

		if(meta.xAxisID===null||!(meta.xAxisIDinscales)||dataset.xAxisID){
			meta.xAxisID=dataset.xAxisID||scalesOpts.xAxes[0].id;
		}
		if(meta.yAxisID===null||!(meta.yAxisIDinscales)||dataset.yAxisID){
			meta.yAxisID=dataset.yAxisID||scalesOpts.yAxes[0].id;
		}
	},

	getDataset:function(){
		returnthis.chart.data.datasets[this.index];
	},

	getMeta:function(){
		returnthis.chart.getDatasetMeta(this.index);
	},

	getScaleForId:function(scaleID){
		returnthis.chart.scales[scaleID];
	},

	/**
	*@private
	*/
	_getValueScaleId:function(){
		returnthis.getMeta().yAxisID;
	},

	/**
	*@private
	*/
	_getIndexScaleId:function(){
		returnthis.getMeta().xAxisID;
	},

	/**
	*@private
	*/
	_getValueScale:function(){
		returnthis.getScaleForId(this._getValueScaleId());
	},

	/**
	*@private
	*/
	_getIndexScale:function(){
		returnthis.getScaleForId(this._getIndexScaleId());
	},

	reset:function(){
		this._update(true);
	},

	/**
	*@private
	*/
	destroy:function(){
		if(this._data){
			unlistenArrayEvents(this._data,this);
		}
	},

	createMetaDataset:function(){
		varme=this;
		vartype=me.datasetElementType;
		returntype&&newtype({
			_chart:me.chart,
			_datasetIndex:me.index
		});
	},

	createMetaData:function(index){
		varme=this;
		vartype=me.dataElementType;
		returntype&&newtype({
			_chart:me.chart,
			_datasetIndex:me.index,
			_index:index
		});
	},

	addElements:function(){
		varme=this;
		varmeta=me.getMeta();
		vardata=me.getDataset().data||[];
		varmetaData=meta.data;
		vari,ilen;

		for(i=0,ilen=data.length;i<ilen;++i){
			metaData[i]=metaData[i]||me.createMetaData(i);
		}

		meta.dataset=meta.dataset||me.createMetaDataset();
	},

	addElementAndReset:function(index){
		varelement=this.createMetaData(index);
		this.getMeta().data.splice(index,0,element);
		this.updateElement(element,index,true);
	},

	buildOrUpdateElements:function(){
		varme=this;
		vardataset=me.getDataset();
		vardata=dataset.data||(dataset.data=[]);

		//Inordertocorrectlyhandledataaddition/deletionanimation(anthussimulate
		//real-timecharts),weneedtomonitorthesedatamodificationsandsynchronize
		//theinternalmetadataaccordingly.
		if(me._data!==data){
			if(me._data){
				//Thiscasehappenswhentheuserreplacedthedataarrayinstance.
				unlistenArrayEvents(me._data,me);
			}

			if(data&&Object.isExtensible(data)){
				listenArrayEvents(data,me);
			}
			me._data=data;
		}

		//Re-syncmetadataincasetheuserreplacedthedataarrayorifwemissed
		//anyupdatesandsomakesurethatwehandlenumberofdatapointschanging.
		me.resyncElements();
	},

	/**
	*Returnsthemergeduser-suppliedanddefaultdataset-leveloptions
	*@private
	*/
	_configure:function(){
		varme=this;
		me._config=helpers$1.merge(Object.create(null),[
			me.chart.options.datasets[me._type],
			me.getDataset(),
		],{
			merger:function(key,target,source){
				if(key!=='_meta'&&key!=='data'){
					helpers$1._merger(key,target,source);
				}
			}
		});
	},

	_update:function(reset){
		varme=this;
		me._configure();
		me._cachedDataOpts=null;
		me.update(reset);
	},

	update:helpers$1.noop,

	transition:function(easingValue){
		varmeta=this.getMeta();
		varelements=meta.data||[];
		varilen=elements.length;
		vari=0;

		for(;i<ilen;++i){
			elements[i].transition(easingValue);
		}

		if(meta.dataset){
			meta.dataset.transition(easingValue);
		}
	},

	draw:function(){
		varmeta=this.getMeta();
		varelements=meta.data||[];
		varilen=elements.length;
		vari=0;

		if(meta.dataset){
			meta.dataset.draw();
		}

		for(;i<ilen;++i){
			elements[i].draw();
		}
	},

	/**
	*Returnsasetofpredefinedstylepropertiesthatshouldbeusedtorepresentthedataset
	*orthedataiftheindexisspecified
	*@param{number}index-dataindex
	*@return{IStyleInterface}styleobject
	*/
	getStyle:function(index){
		varme=this;
		varmeta=me.getMeta();
		vardataset=meta.dataset;
		varstyle;

		me._configure();
		if(dataset&&index===undefined){
			style=me._resolveDatasetElementOptions(dataset||{});
		}else{
			index=index||0;
			style=me._resolveDataElementOptions(meta.data[index]||{},index);
		}

		if(style.fill===false||style.fill===null){
			style.backgroundColor=style.borderColor;
		}

		returnstyle;
	},

	/**
	*@private
	*/
	_resolveDatasetElementOptions:function(element,hover){
		varme=this;
		varchart=me.chart;
		vardatasetOpts=me._config;
		varcustom=element.custom||{};
		varoptions=chart.options.elements[me.datasetElementType.prototype._type]||{};
		varelementOptions=me._datasetElementOptions;
		varvalues={};
		vari,ilen,key,readKey;

		//Scriptableoptions
		varcontext={
			chart:chart,
			dataset:me.getDataset(),
			datasetIndex:me.index,
			hover:hover
		};

		for(i=0,ilen=elementOptions.length;i<ilen;++i){
			key=elementOptions[i];
			readKey=hover?'hover'+key.charAt(0).toUpperCase()+key.slice(1):key;
			values[key]=resolve([
				custom[readKey],
				datasetOpts[readKey],
				options[readKey]
			],context);
		}

		returnvalues;
	},

	/**
	*@private
	*/
	_resolveDataElementOptions:function(element,index){
		varme=this;
		varcustom=element&&element.custom;
		varcached=me._cachedDataOpts;
		if(cached&&!custom){
			returncached;
		}
		varchart=me.chart;
		vardatasetOpts=me._config;
		varoptions=chart.options.elements[me.dataElementType.prototype._type]||{};
		varelementOptions=me._dataElementOptions;
		varvalues={};

		//Scriptableoptions
		varcontext={
			chart:chart,
			dataIndex:index,
			dataset:me.getDataset(),
			datasetIndex:me.index
		};

		//`resolve`setscacheableto`false`ifanyoptionisindexedorscripted
		varinfo={cacheable:!custom};

		varkeys,i,ilen,key;

		custom=custom||{};

		if(helpers$1.isArray(elementOptions)){
			for(i=0,ilen=elementOptions.length;i<ilen;++i){
				key=elementOptions[i];
				values[key]=resolve([
					custom[key],
					datasetOpts[key],
					options[key]
				],context,index,info);
			}
		}else{
			keys=Object.keys(elementOptions);
			for(i=0,ilen=keys.length;i<ilen;++i){
				key=keys[i];
				values[key]=resolve([
					custom[key],
					datasetOpts[elementOptions[key]],
					datasetOpts[key],
					options[key]
				],context,index,info);
			}
		}

		if(info.cacheable){
			me._cachedDataOpts=Object.freeze(values);
		}

		returnvalues;
	},

	removeHoverStyle:function(element){
		helpers$1.merge(element._model,element.$previousStyle||{});
		deleteelement.$previousStyle;
	},

	setHoverStyle:function(element){
		vardataset=this.chart.data.datasets[element._datasetIndex];
		varindex=element._index;
		varcustom=element.custom||{};
		varmodel=element._model;
		vargetHoverColor=helpers$1.getHoverColor;

		element.$previousStyle={
			backgroundColor:model.backgroundColor,
			borderColor:model.borderColor,
			borderWidth:model.borderWidth
		};

		model.backgroundColor=resolve([custom.hoverBackgroundColor,dataset.hoverBackgroundColor,getHoverColor(model.backgroundColor)],undefined,index);
		model.borderColor=resolve([custom.hoverBorderColor,dataset.hoverBorderColor,getHoverColor(model.borderColor)],undefined,index);
		model.borderWidth=resolve([custom.hoverBorderWidth,dataset.hoverBorderWidth,model.borderWidth],undefined,index);
	},

	/**
	*@private
	*/
	_removeDatasetHoverStyle:function(){
		varelement=this.getMeta().dataset;

		if(element){
			this.removeHoverStyle(element);
		}
	},

	/**
	*@private
	*/
	_setDatasetHoverStyle:function(){
		varelement=this.getMeta().dataset;
		varprev={};
		vari,ilen,key,keys,hoverOptions,model;

		if(!element){
			return;
		}

		model=element._model;
		hoverOptions=this._resolveDatasetElementOptions(element,true);

		keys=Object.keys(hoverOptions);
		for(i=0,ilen=keys.length;i<ilen;++i){
			key=keys[i];
			prev[key]=model[key];
			model[key]=hoverOptions[key];
		}

		element.$previousStyle=prev;
	},

	/**
	*@private
	*/
	resyncElements:function(){
		varme=this;
		varmeta=me.getMeta();
		vardata=me.getDataset().data;
		varnumMeta=meta.data.length;
		varnumData=data.length;

		if(numData<numMeta){
			meta.data.splice(numData,numMeta-numData);
		}elseif(numData>numMeta){
			me.insertElements(numMeta,numData-numMeta);
		}
	},

	/**
	*@private
	*/
	insertElements:function(start,count){
		for(vari=0;i<count;++i){
			this.addElementAndReset(start+i);
		}
	},

	/**
	*@private
	*/
	onDataPush:function(){
		varcount=arguments.length;
		this.insertElements(this.getDataset().data.length-count,count);
	},

	/**
	*@private
	*/
	onDataPop:function(){
		this.getMeta().data.pop();
	},

	/**
	*@private
	*/
	onDataShift:function(){
		this.getMeta().data.shift();
	},

	/**
	*@private
	*/
	onDataSplice:function(start,count){
		this.getMeta().data.splice(start,count);
		this.insertElements(start,arguments.length-2);
	},

	/**
	*@private
	*/
	onDataUnshift:function(){
		this.insertElements(0,arguments.length);
	}
});

DatasetController.extend=helpers$1.inherits;

varcore_datasetController=DatasetController;

varTAU=Math.PI*2;

core_defaults._set('global',{
	elements:{
		arc:{
			backgroundColor:core_defaults.global.defaultColor,
			borderColor:'#fff',
			borderWidth:2,
			borderAlign:'center'
		}
	}
});

functionclipArc(ctx,arc){
	varstartAngle=arc.startAngle;
	varendAngle=arc.endAngle;
	varpixelMargin=arc.pixelMargin;
	varangleMargin=pixelMargin/arc.outerRadius;
	varx=arc.x;
	vary=arc.y;

	//Drawaninnerborderbyclipingthearcanddrawingadouble-widthborder
	//Enlargetheclippingarcby0.33pixelstoeliminateglitchesbetweenborders
	ctx.beginPath();
	ctx.arc(x,y,arc.outerRadius,startAngle-angleMargin,endAngle+angleMargin);
	if(arc.innerRadius>pixelMargin){
		angleMargin=pixelMargin/arc.innerRadius;
		ctx.arc(x,y,arc.innerRadius-pixelMargin,endAngle+angleMargin,startAngle-angleMargin,true);
	}else{
		ctx.arc(x,y,pixelMargin,endAngle+Math.PI/2,startAngle-Math.PI/2);
	}
	ctx.closePath();
	ctx.clip();
}

functiondrawFullCircleBorders(ctx,vm,arc,inner){
	varendAngle=arc.endAngle;
	vari;

	if(inner){
		arc.endAngle=arc.startAngle+TAU;
		clipArc(ctx,arc);
		arc.endAngle=endAngle;
		if(arc.endAngle===arc.startAngle&&arc.fullCircles){
			arc.endAngle+=TAU;
			arc.fullCircles--;
		}
	}

	ctx.beginPath();
	ctx.arc(arc.x,arc.y,arc.innerRadius,arc.startAngle+TAU,arc.startAngle,true);
	for(i=0;i<arc.fullCircles;++i){
		ctx.stroke();
	}

	ctx.beginPath();
	ctx.arc(arc.x,arc.y,vm.outerRadius,arc.startAngle,arc.startAngle+TAU);
	for(i=0;i<arc.fullCircles;++i){
		ctx.stroke();
	}
}

functiondrawBorder(ctx,vm,arc){
	varinner=vm.borderAlign==='inner';

	if(inner){
		ctx.lineWidth=vm.borderWidth*2;
		ctx.lineJoin='round';
	}else{
		ctx.lineWidth=vm.borderWidth;
		ctx.lineJoin='bevel';
	}

	if(arc.fullCircles){
		drawFullCircleBorders(ctx,vm,arc,inner);
	}

	if(inner){
		clipArc(ctx,arc);
	}

	ctx.beginPath();
	ctx.arc(arc.x,arc.y,vm.outerRadius,arc.startAngle,arc.endAngle);
	ctx.arc(arc.x,arc.y,arc.innerRadius,arc.endAngle,arc.startAngle,true);
	ctx.closePath();
	ctx.stroke();
}

varelement_arc=core_element.extend({
	_type:'arc',

	inLabelRange:function(mouseX){
		varvm=this._view;

		if(vm){
			return(Math.pow(mouseX-vm.x,2)<Math.pow(vm.radius+vm.hoverRadius,2));
		}
		returnfalse;
	},

	inRange:function(chartX,chartY){
		varvm=this._view;

		if(vm){
			varpointRelativePosition=helpers$1.getAngleFromPoint(vm,{x:chartX,y:chartY});
			varangle=pointRelativePosition.angle;
			vardistance=pointRelativePosition.distance;

			//Sanitiseanglerange
			varstartAngle=vm.startAngle;
			varendAngle=vm.endAngle;
			while(endAngle<startAngle){
				endAngle+=TAU;
			}
			while(angle>endAngle){
				angle-=TAU;
			}
			while(angle<startAngle){
				angle+=TAU;
			}

			//Checkifwithintherangeoftheopen/closeangle
			varbetweenAngles=(angle>=startAngle&&angle<=endAngle);
			varwithinRadius=(distance>=vm.innerRadius&&distance<=vm.outerRadius);

			return(betweenAngles&&withinRadius);
		}
		returnfalse;
	},

	getCenterPoint:function(){
		varvm=this._view;
		varhalfAngle=(vm.startAngle+vm.endAngle)/2;
		varhalfRadius=(vm.innerRadius+vm.outerRadius)/2;
		return{
			x:vm.x+Math.cos(halfAngle)*halfRadius,
			y:vm.y+Math.sin(halfAngle)*halfRadius
		};
	},

	getArea:function(){
		varvm=this._view;
		returnMath.PI*((vm.endAngle-vm.startAngle)/(2*Math.PI))*(Math.pow(vm.outerRadius,2)-Math.pow(vm.innerRadius,2));
	},

	tooltipPosition:function(){
		varvm=this._view;
		varcentreAngle=vm.startAngle+((vm.endAngle-vm.startAngle)/2);
		varrangeFromCentre=(vm.outerRadius-vm.innerRadius)/2+vm.innerRadius;

		return{
			x:vm.x+(Math.cos(centreAngle)*rangeFromCentre),
			y:vm.y+(Math.sin(centreAngle)*rangeFromCentre)
		};
	},

	draw:function(){
		varctx=this._chart.ctx;
		varvm=this._view;
		varpixelMargin=(vm.borderAlign==='inner')?0.33:0;
		vararc={
			x:vm.x,
			y:vm.y,
			innerRadius:vm.innerRadius,
			outerRadius:Math.max(vm.outerRadius-pixelMargin,0),
			pixelMargin:pixelMargin,
			startAngle:vm.startAngle,
			endAngle:vm.endAngle,
			fullCircles:Math.floor(vm.circumference/TAU)
		};
		vari;

		ctx.save();

		ctx.fillStyle=vm.backgroundColor;
		ctx.strokeStyle=vm.borderColor;

		if(arc.fullCircles){
			arc.endAngle=arc.startAngle+TAU;
			ctx.beginPath();
			ctx.arc(arc.x,arc.y,arc.outerRadius,arc.startAngle,arc.endAngle);
			ctx.arc(arc.x,arc.y,arc.innerRadius,arc.endAngle,arc.startAngle,true);
			ctx.closePath();
			for(i=0;i<arc.fullCircles;++i){
				ctx.fill();
			}
			arc.endAngle=arc.startAngle+vm.circumference%TAU;
		}

		ctx.beginPath();
		ctx.arc(arc.x,arc.y,arc.outerRadius,arc.startAngle,arc.endAngle);
		ctx.arc(arc.x,arc.y,arc.innerRadius,arc.endAngle,arc.startAngle,true);
		ctx.closePath();
		ctx.fill();

		if(vm.borderWidth){
			drawBorder(ctx,vm,arc);
		}

		ctx.restore();
	}
});

varvalueOrDefault$1=helpers$1.valueOrDefault;

vardefaultColor=core_defaults.global.defaultColor;

core_defaults._set('global',{
	elements:{
		line:{
			tension:0.4,
			backgroundColor:defaultColor,
			borderWidth:3,
			borderColor:defaultColor,
			borderCapStyle:'butt',
			borderDash:[],
			borderDashOffset:0.0,
			borderJoinStyle:'miter',
			capBezierPoints:true,
			fill:true,//dowefillintheareabetweenthelineanditsbaseaxis
		}
	}
});

varelement_line=core_element.extend({
	_type:'line',

	draw:function(){
		varme=this;
		varvm=me._view;
		varctx=me._chart.ctx;
		varspanGaps=vm.spanGaps;
		varpoints=me._children.slice();//clonearray
		varglobalDefaults=core_defaults.global;
		varglobalOptionLineElements=globalDefaults.elements.line;
		varlastDrawnIndex=-1;
		varclosePath=me._loop;
		varindex,previous,currentVM;

		if(!points.length){
			return;
		}

		if(me._loop){
			for(index=0;index<points.length;++index){
				previous=helpers$1.previousItem(points,index);
				//Ifthelinehasanopenpath,shiftthepointarray
				if(!points[index]._view.skip&&previous._view.skip){
					points=points.slice(index).concat(points.slice(0,index));
					closePath=spanGaps;
					break;
				}
			}
			//Ifthelinehasaclosepath,addthefirstpointagain
			if(closePath){
				points.push(points[0]);
			}
		}

		ctx.save();

		//StrokeLineOptions
		ctx.lineCap=vm.borderCapStyle||globalOptionLineElements.borderCapStyle;

		//IE9and10donotsupportlinedash
		if(ctx.setLineDash){
			ctx.setLineDash(vm.borderDash||globalOptionLineElements.borderDash);
		}

		ctx.lineDashOffset=valueOrDefault$1(vm.borderDashOffset,globalOptionLineElements.borderDashOffset);
		ctx.lineJoin=vm.borderJoinStyle||globalOptionLineElements.borderJoinStyle;
		ctx.lineWidth=valueOrDefault$1(vm.borderWidth,globalOptionLineElements.borderWidth);
		ctx.strokeStyle=vm.borderColor||globalDefaults.defaultColor;

		//StrokeLine
		ctx.beginPath();

		//Firstpointmovestoit'sstartingpositionnomatterwhat
		currentVM=points[0]._view;
		if(!currentVM.skip){
			ctx.moveTo(currentVM.x,currentVM.y);
			lastDrawnIndex=0;
		}

		for(index=1;index<points.length;++index){
			currentVM=points[index]._view;
			previous=lastDrawnIndex===-1?helpers$1.previousItem(points,index):points[lastDrawnIndex];

			if(!currentVM.skip){
				if((lastDrawnIndex!==(index-1)&&!spanGaps)||lastDrawnIndex===-1){
					//Therewasagapandthisisthefirstpointafterthegap
					ctx.moveTo(currentVM.x,currentVM.y);
				}else{
					//Linetonextpoint
					helpers$1.canvas.lineTo(ctx,previous._view,currentVM);
				}
				lastDrawnIndex=index;
			}
		}

		if(closePath){
			ctx.closePath();
		}

		ctx.stroke();
		ctx.restore();
	}
});

varvalueOrDefault$2=helpers$1.valueOrDefault;

vardefaultColor$1=core_defaults.global.defaultColor;

core_defaults._set('global',{
	elements:{
		point:{
			radius:3,
			pointStyle:'circle',
			backgroundColor:defaultColor$1,
			borderColor:defaultColor$1,
			borderWidth:1,
			//Hover
			hitRadius:1,
			hoverRadius:4,
			hoverBorderWidth:1
		}
	}
});

functionxRange(mouseX){
	varvm=this._view;
	returnvm?(Math.abs(mouseX-vm.x)<vm.radius+vm.hitRadius):false;
}

functionyRange(mouseY){
	varvm=this._view;
	returnvm?(Math.abs(mouseY-vm.y)<vm.radius+vm.hitRadius):false;
}

varelement_point=core_element.extend({
	_type:'point',

	inRange:function(mouseX,mouseY){
		varvm=this._view;
		returnvm?((Math.pow(mouseX-vm.x,2)+Math.pow(mouseY-vm.y,2))<Math.pow(vm.hitRadius+vm.radius,2)):false;
	},

	inLabelRange:xRange,
	inXRange:xRange,
	inYRange:yRange,

	getCenterPoint:function(){
		varvm=this._view;
		return{
			x:vm.x,
			y:vm.y
		};
	},

	getArea:function(){
		returnMath.PI*Math.pow(this._view.radius,2);
	},

	tooltipPosition:function(){
		varvm=this._view;
		return{
			x:vm.x,
			y:vm.y,
			padding:vm.radius+vm.borderWidth
		};
	},

	draw:function(chartArea){
		varvm=this._view;
		varctx=this._chart.ctx;
		varpointStyle=vm.pointStyle;
		varrotation=vm.rotation;
		varradius=vm.radius;
		varx=vm.x;
		vary=vm.y;
		varglobalDefaults=core_defaults.global;
		vardefaultColor=globalDefaults.defaultColor;//eslint-disable-lineno-shadow

		if(vm.skip){
			return;
		}

		//ClippingforPoints.
		if(chartArea===undefined||helpers$1.canvas._isPointInArea(vm,chartArea)){
			ctx.strokeStyle=vm.borderColor||defaultColor;
			ctx.lineWidth=valueOrDefault$2(vm.borderWidth,globalDefaults.elements.point.borderWidth);
			ctx.fillStyle=vm.backgroundColor||defaultColor;
			helpers$1.canvas.drawPoint(ctx,pointStyle,radius,x,y,rotation);
		}
	}
});

vardefaultColor$2=core_defaults.global.defaultColor;

core_defaults._set('global',{
	elements:{
		rectangle:{
			backgroundColor:defaultColor$2,
			borderColor:defaultColor$2,
			borderSkipped:'bottom',
			borderWidth:0
		}
	}
});

functionisVertical(vm){
	returnvm&&vm.width!==undefined;
}

/**
 *Helperfunctiontogettheboundsofthebarregardlessoftheorientation
 *@parambar{Chart.Element.Rectangle}thebar
 *@return{Bounds}boundsofthebar
 *@private
 */
functiongetBarBounds(vm){
	varx1,x2,y1,y2,half;

	if(isVertical(vm)){
		half=vm.width/2;
		x1=vm.x-half;
		x2=vm.x+half;
		y1=Math.min(vm.y,vm.base);
		y2=Math.max(vm.y,vm.base);
	}else{
		half=vm.height/2;
		x1=Math.min(vm.x,vm.base);
		x2=Math.max(vm.x,vm.base);
		y1=vm.y-half;
		y2=vm.y+half;
	}

	return{
		left:x1,
		top:y1,
		right:x2,
		bottom:y2
	};
}

functionswap(orig,v1,v2){
	returnorig===v1?v2:orig===v2?v1:orig;
}

functionparseBorderSkipped(vm){
	varedge=vm.borderSkipped;
	varres={};

	if(!edge){
		returnres;
	}

	if(vm.horizontal){
		if(vm.base>vm.x){
			edge=swap(edge,'left','right');
		}
	}elseif(vm.base<vm.y){
		edge=swap(edge,'bottom','top');
	}

	res[edge]=true;
	returnres;
}

functionparseBorderWidth(vm,maxW,maxH){
	varvalue=vm.borderWidth;
	varskip=parseBorderSkipped(vm);
	vart,r,b,l;

	if(helpers$1.isObject(value)){
		t=+value.top||0;
		r=+value.right||0;
		b=+value.bottom||0;
		l=+value.left||0;
	}else{
		t=r=b=l=+value||0;
	}

	return{
		t:skip.top||(t<0)?0:t>maxH?maxH:t,
		r:skip.right||(r<0)?0:r>maxW?maxW:r,
		b:skip.bottom||(b<0)?0:b>maxH?maxH:b,
		l:skip.left||(l<0)?0:l>maxW?maxW:l
	};
}

functionboundingRects(vm){
	varbounds=getBarBounds(vm);
	varwidth=bounds.right-bounds.left;
	varheight=bounds.bottom-bounds.top;
	varborder=parseBorderWidth(vm,width/2,height/2);

	return{
		outer:{
			x:bounds.left,
			y:bounds.top,
			w:width,
			h:height
		},
		inner:{
			x:bounds.left+border.l,
			y:bounds.top+border.t,
			w:width-border.l-border.r,
			h:height-border.t-border.b
		}
	};
}

functioninRange(vm,x,y){
	varskipX=x===null;
	varskipY=y===null;
	varbounds=!vm||(skipX&&skipY)?false:getBarBounds(vm);

	returnbounds
		&&(skipX||x>=bounds.left&&x<=bounds.right)
		&&(skipY||y>=bounds.top&&y<=bounds.bottom);
}

varelement_rectangle=core_element.extend({
	_type:'rectangle',

	draw:function(){
		varctx=this._chart.ctx;
		varvm=this._view;
		varrects=boundingRects(vm);
		varouter=rects.outer;
		varinner=rects.inner;

		ctx.fillStyle=vm.backgroundColor;
		ctx.fillRect(outer.x,outer.y,outer.w,outer.h);

		if(outer.w===inner.w&&outer.h===inner.h){
			return;
		}

		ctx.save();
		ctx.beginPath();
		ctx.rect(outer.x,outer.y,outer.w,outer.h);
		ctx.clip();
		ctx.fillStyle=vm.borderColor;
		ctx.rect(inner.x,inner.y,inner.w,inner.h);
		ctx.fill('evenodd');
		ctx.restore();
	},

	height:function(){
		varvm=this._view;
		returnvm.base-vm.y;
	},

	inRange:function(mouseX,mouseY){
		returninRange(this._view,mouseX,mouseY);
	},

	inLabelRange:function(mouseX,mouseY){
		varvm=this._view;
		returnisVertical(vm)
			?inRange(vm,mouseX,null)
			:inRange(vm,null,mouseY);
	},

	inXRange:function(mouseX){
		returninRange(this._view,mouseX,null);
	},

	inYRange:function(mouseY){
		returninRange(this._view,null,mouseY);
	},

	getCenterPoint:function(){
		varvm=this._view;
		varx,y;
		if(isVertical(vm)){
			x=vm.x;
			y=(vm.y+vm.base)/2;
		}else{
			x=(vm.x+vm.base)/2;
			y=vm.y;
		}

		return{x:x,y:y};
	},

	getArea:function(){
		varvm=this._view;

		returnisVertical(vm)
			?vm.width*Math.abs(vm.y-vm.base)
			:vm.height*Math.abs(vm.x-vm.base);
	},

	tooltipPosition:function(){
		varvm=this._view;
		return{
			x:vm.x,
			y:vm.y
		};
	}
});

varelements={};
varArc=element_arc;
varLine=element_line;
varPoint=element_point;
varRectangle=element_rectangle;
elements.Arc=Arc;
elements.Line=Line;
elements.Point=Point;
elements.Rectangle=Rectangle;

vardeprecated=helpers$1._deprecated;
varvalueOrDefault$3=helpers$1.valueOrDefault;

core_defaults._set('bar',{
	hover:{
		mode:'label'
	},

	scales:{
		xAxes:[{
			type:'category',
			offset:true,
			gridLines:{
				offsetGridLines:true
			}
		}],

		yAxes:[{
			type:'linear'
		}]
	}
});

core_defaults._set('global',{
	datasets:{
		bar:{
			categoryPercentage:0.8,
			barPercentage:0.9
		}
	}
});

/**
 *Computesthe"optimal"samplesizetomaintainbarsequallysizedwhilepreventingoverlap.
 *@private
 */
functioncomputeMinSampleSize(scale,pixels){
	varmin=scale._length;
	varprev,curr,i,ilen;

	for(i=1,ilen=pixels.length;i<ilen;++i){
		min=Math.min(min,Math.abs(pixels[i]-pixels[i-1]));
	}

	for(i=0,ilen=scale.getTicks().length;i<ilen;++i){
		curr=scale.getPixelForTick(i);
		min=i>0?Math.min(min,Math.abs(curr-prev)):min;
		prev=curr;
	}

	returnmin;
}

/**
 *Computesan"ideal"categorybasedontheabsolutebarthicknessor,ifundefinedornull,
 *usesthesmallestinterval(seecomputeMinSampleSize)thatpreventsbaroverlapping.This
 *modecurrentlyalwaysgeneratesbarsequallysized(untilweintroducescriptableoptions?).
 *@private
 */
functioncomputeFitCategoryTraits(index,ruler,options){
	varthickness=options.barThickness;
	varcount=ruler.stackCount;
	varcurr=ruler.pixels[index];
	varmin=helpers$1.isNullOrUndef(thickness)
		?computeMinSampleSize(ruler.scale,ruler.pixels)
		:-1;
	varsize,ratio;

	if(helpers$1.isNullOrUndef(thickness)){
		size=min*options.categoryPercentage;
		ratio=options.barPercentage;
	}else{
		//Whenbarthicknessisenforced,categoryandbarpercentagesareignored.
		//Note(SB):wecouldaddsupportforrelativebarthickness(e.g.barThickness:'50%')
		//anddeprecatebarPercentagesincethisvalueisignoredwhenthicknessisabsolute.
		size=thickness*count;
		ratio=1;
	}

	return{
		chunk:size/count,
		ratio:ratio,
		start:curr-(size/2)
	};
}

/**
 *Computesan"optimal"categorythatgloballyarrangesbarssidebyside(nogapwhen
 *percentageoptionsare1),basedonthepreviousandfollowingcategories.Thismode
 *generatesbarswithdifferentwidthswhendataarenotevenlyspaced.
 *@private
 */
functioncomputeFlexCategoryTraits(index,ruler,options){
	varpixels=ruler.pixels;
	varcurr=pixels[index];
	varprev=index>0?pixels[index-1]:null;
	varnext=index<pixels.length-1?pixels[index+1]:null;
	varpercent=options.categoryPercentage;
	varstart,size;

	if(prev===null){
		//firstdata:itssizeisdoublebasedonthenextpointor,
		//ifit'salsothelastdata,weusethescalesize.
		prev=curr-(next===null?ruler.end-ruler.start:next-curr);
	}

	if(next===null){
		//lastdata:itssizeisalsodoublebasedonthepreviouspoint.
		next=curr+curr-prev;
	}

	start=curr-(curr-Math.min(prev,next))/2*percent;
	size=Math.abs(next-prev)/2*percent;

	return{
		chunk:size/ruler.stackCount,
		ratio:options.barPercentage,
		start:start
	};
}

varcontroller_bar=core_datasetController.extend({

	dataElementType:elements.Rectangle,

	/**
	*@private
	*/
	_dataElementOptions:[
		'backgroundColor',
		'borderColor',
		'borderSkipped',
		'borderWidth',
		'barPercentage',
		'barThickness',
		'categoryPercentage',
		'maxBarThickness',
		'minBarLength'
	],

	initialize:function(){
		varme=this;
		varmeta,scaleOpts;

		core_datasetController.prototype.initialize.apply(me,arguments);

		meta=me.getMeta();
		meta.stack=me.getDataset().stack;
		meta.bar=true;

		scaleOpts=me._getIndexScale().options;
		deprecated('barchart',scaleOpts.barPercentage,'scales.[x/y]Axes.barPercentage','dataset.barPercentage');
		deprecated('barchart',scaleOpts.barThickness,'scales.[x/y]Axes.barThickness','dataset.barThickness');
		deprecated('barchart',scaleOpts.categoryPercentage,'scales.[x/y]Axes.categoryPercentage','dataset.categoryPercentage');
		deprecated('barchart',me._getValueScale().options.minBarLength,'scales.[x/y]Axes.minBarLength','dataset.minBarLength');
		deprecated('barchart',scaleOpts.maxBarThickness,'scales.[x/y]Axes.maxBarThickness','dataset.maxBarThickness');
	},

	update:function(reset){
		varme=this;
		varrects=me.getMeta().data;
		vari,ilen;

		me._ruler=me.getRuler();

		for(i=0,ilen=rects.length;i<ilen;++i){
			me.updateElement(rects[i],i,reset);
		}
	},

	updateElement:function(rectangle,index,reset){
		varme=this;
		varmeta=me.getMeta();
		vardataset=me.getDataset();
		varoptions=me._resolveDataElementOptions(rectangle,index);

		rectangle._xScale=me.getScaleForId(meta.xAxisID);
		rectangle._yScale=me.getScaleForId(meta.yAxisID);
		rectangle._datasetIndex=me.index;
		rectangle._index=index;
		rectangle._model={
			backgroundColor:options.backgroundColor,
			borderColor:options.borderColor,
			borderSkipped:options.borderSkipped,
			borderWidth:options.borderWidth,
			datasetLabel:dataset.label,
			label:me.chart.data.labels[index]
		};

		if(helpers$1.isArray(dataset.data[index])){
			rectangle._model.borderSkipped=null;
		}

		me._updateElementGeometry(rectangle,index,reset,options);

		rectangle.pivot();
	},

	/**
	*@private
	*/
	_updateElementGeometry:function(rectangle,index,reset,options){
		varme=this;
		varmodel=rectangle._model;
		varvscale=me._getValueScale();
		varbase=vscale.getBasePixel();
		varhorizontal=vscale.isHorizontal();
		varruler=me._ruler||me.getRuler();
		varvpixels=me.calculateBarValuePixels(me.index,index,options);
		varipixels=me.calculateBarIndexPixels(me.index,index,ruler,options);

		model.horizontal=horizontal;
		model.base=reset?base:vpixels.base;
		model.x=horizontal?reset?base:vpixels.head:ipixels.center;
		model.y=horizontal?ipixels.center:reset?base:vpixels.head;
		model.height=horizontal?ipixels.size:undefined;
		model.width=horizontal?undefined:ipixels.size;
	},

	/**
	*Returnsthestacksbasedongroupsandbarvisibility.
	*@param{number}[last]-Thedatasetindex
	*@returns{string[]}ThelistofstackIDs
	*@private
	*/
	_getStacks:function(last){
		varme=this;
		varscale=me._getIndexScale();
		varmetasets=scale._getMatchingVisibleMetas(me._type);
		varstacked=scale.options.stacked;
		varilen=metasets.length;
		varstacks=[];
		vari,meta;

		for(i=0;i<ilen;++i){
			meta=metasets[i];
			//stacked  |meta.stack
			//          |found|notfound|undefined
			//false    |  x  |    x    |    x
			//true     |      |    x    |
			//undefined|      |    x    |    x
			if(stacked===false||stacks.indexOf(meta.stack)===-1||
				(stacked===undefined&&meta.stack===undefined)){
				stacks.push(meta.stack);
			}
			if(meta.index===last){
				break;
			}
		}

		returnstacks;
	},

	/**
	*Returnstheeffectivenumberofstacksbasedongroupsandbarvisibility.
	*@private
	*/
	getStackCount:function(){
		returnthis._getStacks().length;
	},

	/**
	*Returnsthestackindexforthegivendatasetbasedongroupsandbarvisibility.
	*@param{number}[datasetIndex]-Thedatasetindex
	*@param{string}[name]-Thestacknametofind
	*@returns{number}Thestackindex
	*@private
	*/
	getStackIndex:function(datasetIndex,name){
		varstacks=this._getStacks(datasetIndex);
		varindex=(name!==undefined)
			?stacks.indexOf(name)
			:-1;//indexOfreturns-1ifelementisnotpresent

		return(index===-1)
			?stacks.length-1
			:index;
	},

	/**
	*@private
	*/
	getRuler:function(){
		varme=this;
		varscale=me._getIndexScale();
		varpixels=[];
		vari,ilen;

		for(i=0,ilen=me.getMeta().data.length;i<ilen;++i){
			pixels.push(scale.getPixelForValue(null,i,me.index));
		}

		return{
			pixels:pixels,
			start:scale._startPixel,
			end:scale._endPixel,
			stackCount:me.getStackCount(),
			scale:scale
		};
	},

	/**
	*Note:pixelvaluesarenotclampedtothescalearea.
	*@private
	*/
	calculateBarValuePixels:function(datasetIndex,index,options){
		varme=this;
		varchart=me.chart;
		varscale=me._getValueScale();
		varisHorizontal=scale.isHorizontal();
		vardatasets=chart.data.datasets;
		varmetasets=scale._getMatchingVisibleMetas(me._type);
		varvalue=scale._parseValue(datasets[datasetIndex].data[index]);
		varminBarLength=options.minBarLength;
		varstacked=scale.options.stacked;
		varstack=me.getMeta().stack;
		varstart=value.start===undefined?0:value.max>=0&&value.min>=0?value.min:value.max;
		varlength=value.start===undefined?value.end:value.max>=0&&value.min>=0?value.max-value.min:value.min-value.max;
		varilen=metasets.length;
		vari,imeta,ivalue,base,head,size,stackLength;

		if(stacked||(stacked===undefined&&stack!==undefined)){
			for(i=0;i<ilen;++i){
				imeta=metasets[i];

				if(imeta.index===datasetIndex){
					break;
				}

				if(imeta.stack===stack){
					stackLength=scale._parseValue(datasets[imeta.index].data[index]);
					ivalue=stackLength.start===undefined?stackLength.end:stackLength.min>=0&&stackLength.max>=0?stackLength.max:stackLength.min;

					if((value.min<0&&ivalue<0)||(value.max>=0&&ivalue>0)){
						start+=ivalue;
					}
				}
			}
		}

		base=scale.getPixelForValue(start);
		head=scale.getPixelForValue(start+length);
		size=head-base;

		if(minBarLength!==undefined&&Math.abs(size)<minBarLength){
			size=minBarLength;
			if(length>=0&&!isHorizontal||length<0&&isHorizontal){
				head=base-minBarLength;
			}else{
				head=base+minBarLength;
			}
		}

		return{
			size:size,
			base:base,
			head:head,
			center:head+size/2
		};
	},

	/**
	*@private
	*/
	calculateBarIndexPixels:function(datasetIndex,index,ruler,options){
		varme=this;
		varrange=options.barThickness==='flex'
			?computeFlexCategoryTraits(index,ruler,options)
			:computeFitCategoryTraits(index,ruler,options);

		varstackIndex=me.getStackIndex(datasetIndex,me.getMeta().stack);
		varcenter=range.start+(range.chunk*stackIndex)+(range.chunk/2);
		varsize=Math.min(
			valueOrDefault$3(options.maxBarThickness,Infinity),
			range.chunk*range.ratio);

		return{
			base:center-size/2,
			head:center+size/2,
			center:center,
			size:size
		};
	},

	draw:function(){
		varme=this;
		varchart=me.chart;
		varscale=me._getValueScale();
		varrects=me.getMeta().data;
		vardataset=me.getDataset();
		varilen=rects.length;
		vari=0;

		helpers$1.canvas.clipArea(chart.ctx,chart.chartArea);

		for(;i<ilen;++i){
			varval=scale._parseValue(dataset.data[i]);
			if(!isNaN(val.min)&&!isNaN(val.max)){
				rects[i].draw();
			}
		}

		helpers$1.canvas.unclipArea(chart.ctx);
	},

	/**
	*@private
	*/
	_resolveDataElementOptions:function(){
		varme=this;
		varvalues=helpers$1.extend({},core_datasetController.prototype._resolveDataElementOptions.apply(me,arguments));
		varindexOpts=me._getIndexScale().options;
		varvalueOpts=me._getValueScale().options;

		values.barPercentage=valueOrDefault$3(indexOpts.barPercentage,values.barPercentage);
		values.barThickness=valueOrDefault$3(indexOpts.barThickness,values.barThickness);
		values.categoryPercentage=valueOrDefault$3(indexOpts.categoryPercentage,values.categoryPercentage);
		values.maxBarThickness=valueOrDefault$3(indexOpts.maxBarThickness,values.maxBarThickness);
		values.minBarLength=valueOrDefault$3(valueOpts.minBarLength,values.minBarLength);

		returnvalues;
	}

});

varvalueOrDefault$4=helpers$1.valueOrDefault;
varresolve$1=helpers$1.options.resolve;

core_defaults._set('bubble',{
	hover:{
		mode:'single'
	},

	scales:{
		xAxes:[{
			type:'linear',//bubbleshouldprobablyusealinearscalebydefault
			position:'bottom',
			id:'x-axis-0'//needanIDsodatasetscanreferencethescale
		}],
		yAxes:[{
			type:'linear',
			position:'left',
			id:'y-axis-0'
		}]
	},

	tooltips:{
		callbacks:{
			title:function(){
				//Titledoesn'tmakesenseforscattersinceweformatthedataasapoint
				return'';
			},
			label:function(item,data){
				vardatasetLabel=data.datasets[item.datasetIndex].label||'';
				vardataPoint=data.datasets[item.datasetIndex].data[item.index];
				returndatasetLabel+':('+item.xLabel+','+item.yLabel+','+dataPoint.r+')';
			}
		}
	}
});

varcontroller_bubble=core_datasetController.extend({
	/**
	*@protected
	*/
	dataElementType:elements.Point,

	/**
	*@private
	*/
	_dataElementOptions:[
		'backgroundColor',
		'borderColor',
		'borderWidth',
		'hoverBackgroundColor',
		'hoverBorderColor',
		'hoverBorderWidth',
		'hoverRadius',
		'hitRadius',
		'pointStyle',
		'rotation'
	],

	/**
	*@protected
	*/
	update:function(reset){
		varme=this;
		varmeta=me.getMeta();
		varpoints=meta.data;

		//UpdatePoints
		helpers$1.each(points,function(point,index){
			me.updateElement(point,index,reset);
		});
	},

	/**
	*@protected
	*/
	updateElement:function(point,index,reset){
		varme=this;
		varmeta=me.getMeta();
		varcustom=point.custom||{};
		varxScale=me.getScaleForId(meta.xAxisID);
		varyScale=me.getScaleForId(meta.yAxisID);
		varoptions=me._resolveDataElementOptions(point,index);
		vardata=me.getDataset().data[index];
		vardsIndex=me.index;

		varx=reset?xScale.getPixelForDecimal(0.5):xScale.getPixelForValue(typeofdata==='object'?data:NaN,index,dsIndex);
		vary=reset?yScale.getBasePixel():yScale.getPixelForValue(data,index,dsIndex);

		point._xScale=xScale;
		point._yScale=yScale;
		point._options=options;
		point._datasetIndex=dsIndex;
		point._index=index;
		point._model={
			backgroundColor:options.backgroundColor,
			borderColor:options.borderColor,
			borderWidth:options.borderWidth,
			hitRadius:options.hitRadius,
			pointStyle:options.pointStyle,
			rotation:options.rotation,
			radius:reset?0:options.radius,
			skip:custom.skip||isNaN(x)||isNaN(y),
			x:x,
			y:y,
		};

		point.pivot();
	},

	/**
	*@protected
	*/
	setHoverStyle:function(point){
		varmodel=point._model;
		varoptions=point._options;
		vargetHoverColor=helpers$1.getHoverColor;

		point.$previousStyle={
			backgroundColor:model.backgroundColor,
			borderColor:model.borderColor,
			borderWidth:model.borderWidth,
			radius:model.radius
		};

		model.backgroundColor=valueOrDefault$4(options.hoverBackgroundColor,getHoverColor(options.backgroundColor));
		model.borderColor=valueOrDefault$4(options.hoverBorderColor,getHoverColor(options.borderColor));
		model.borderWidth=valueOrDefault$4(options.hoverBorderWidth,options.borderWidth);
		model.radius=options.radius+options.hoverRadius;
	},

	/**
	*@private
	*/
	_resolveDataElementOptions:function(point,index){
		varme=this;
		varchart=me.chart;
		vardataset=me.getDataset();
		varcustom=point.custom||{};
		vardata=dataset.data[index]||{};
		varvalues=core_datasetController.prototype._resolveDataElementOptions.apply(me,arguments);

		//Scriptableoptions
		varcontext={
			chart:chart,
			dataIndex:index,
			dataset:dataset,
			datasetIndex:me.index
		};

		//Incasevalueswerecached(andthusfrozen),weneedtoclonethevalues
		if(me._cachedDataOpts===values){
			values=helpers$1.extend({},values);
		}

		//Customradiusresolution
		values.radius=resolve$1([
			custom.radius,
			data.r,
			me._config.radius,
			chart.options.elements.point.radius
		],context,index);

		returnvalues;
	}
});

varvalueOrDefault$5=helpers$1.valueOrDefault;

varPI$1=Math.PI;
varDOUBLE_PI$1=PI$1*2;
varHALF_PI$1=PI$1/2;

core_defaults._set('doughnut',{
	animation:{
		//Boolean-WhetherweanimatetherotationoftheDoughnut
		animateRotate:true,
		//Boolean-WhetherweanimatescalingtheDoughnutfromthecentre
		animateScale:false
	},
	hover:{
		mode:'single'
	},
	legendCallback:function(chart){
		varlist=document.createElement('ul');
		vardata=chart.data;
		vardatasets=data.datasets;
		varlabels=data.labels;
		vari,ilen,listItem,listItemSpan;

		list.setAttribute('class',chart.id+'-legend');
		if(datasets.length){
			for(i=0,ilen=datasets[0].data.length;i<ilen;++i){
				listItem=list.appendChild(document.createElement('li'));
				listItemSpan=listItem.appendChild(document.createElement('span'));
				listItemSpan.style.backgroundColor=datasets[0].backgroundColor[i];
				if(labels[i]){
					listItem.appendChild(document.createTextNode(labels[i]));
				}
			}
		}

		returnlist.outerHTML;
	},
	legend:{
		labels:{
			generateLabels:function(chart){
				vardata=chart.data;
				if(data.labels.length&&data.datasets.length){
					returndata.labels.map(function(label,i){
						varmeta=chart.getDatasetMeta(0);
						varstyle=meta.controller.getStyle(i);

						return{
							text:label,
							fillStyle:style.backgroundColor,
							strokeStyle:style.borderColor,
							lineWidth:style.borderWidth,
							hidden:isNaN(data.datasets[0].data[i])||meta.data[i].hidden,

							//Extradatausedfortogglingthecorrectitem
							index:i
						};
					});
				}
				return[];
			}
		},

		onClick:function(e,legendItem){
			varindex=legendItem.index;
			varchart=this.chart;
			vari,ilen,meta;

			for(i=0,ilen=(chart.data.datasets||[]).length;i<ilen;++i){
				meta=chart.getDatasetMeta(i);
				//togglevisibilityofindexifexists
				if(meta.data[index]){
					meta.data[index].hidden=!meta.data[index].hidden;
				}
			}

			chart.update();
		}
	},

	//Thepercentageofthechartthatwecutoutofthemiddle.
	cutoutPercentage:50,

	//Therotationofthechart,wherethefirstdataarcbegins.
	rotation:-HALF_PI$1,

	//Thetotalcircumferenceofthechart.
	circumference:DOUBLE_PI$1,

	//Needtooverridethesetogiveanicedefault
	tooltips:{
		callbacks:{
			title:function(){
				return'';
			},
			label:function(tooltipItem,data){
				vardataLabel=data.labels[tooltipItem.index];
				varvalue=':'+data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];

				if(helpers$1.isArray(dataLabel)){
					//showvalueonfirstlineofmultilinelabel
					//needtoclonebecausewearechangingthevalue
					dataLabel=dataLabel.slice();
					dataLabel[0]+=value;
				}else{
					dataLabel+=value;
				}

				returndataLabel;
			}
		}
	}
});

varcontroller_doughnut=core_datasetController.extend({

	dataElementType:elements.Arc,

	linkScales:helpers$1.noop,

	/**
	*@private
	*/
	_dataElementOptions:[
		'backgroundColor',
		'borderColor',
		'borderWidth',
		'borderAlign',
		'hoverBackgroundColor',
		'hoverBorderColor',
		'hoverBorderWidth',
	],

	//Getindexofthedatasetinrelationtothevisibledatasets.Thisallowsdeterminingtheinnerandouterradiuscorrectly
	getRingIndex:function(datasetIndex){
		varringIndex=0;

		for(varj=0;j<datasetIndex;++j){
			if(this.chart.isDatasetVisible(j)){
				++ringIndex;
			}
		}

		returnringIndex;
	},

	update:function(reset){
		varme=this;
		varchart=me.chart;
		varchartArea=chart.chartArea;
		varopts=chart.options;
		varratioX=1;
		varratioY=1;
		varoffsetX=0;
		varoffsetY=0;
		varmeta=me.getMeta();
		vararcs=meta.data;
		varcutout=opts.cutoutPercentage/100||0;
		varcircumference=opts.circumference;
		varchartWeight=me._getRingWeight(me.index);
		varmaxWidth,maxHeight,i,ilen;

		//Ifthechart'scircumferenceisn'tafullcircle,calculatesizeasaratioofthewidth/heightofthearc
		if(circumference<DOUBLE_PI$1){
			varstartAngle=opts.rotation%DOUBLE_PI$1;
			startAngle+=startAngle>=PI$1?-DOUBLE_PI$1:startAngle<-PI$1?DOUBLE_PI$1:0;
			varendAngle=startAngle+circumference;
			varstartX=Math.cos(startAngle);
			varstartY=Math.sin(startAngle);
			varendX=Math.cos(endAngle);
			varendY=Math.sin(endAngle);
			varcontains0=(startAngle<=0&&endAngle>=0)||endAngle>=DOUBLE_PI$1;
			varcontains90=(startAngle<=HALF_PI$1&&endAngle>=HALF_PI$1)||endAngle>=DOUBLE_PI$1+HALF_PI$1;
			varcontains180=startAngle===-PI$1||endAngle>=PI$1;
			varcontains270=(startAngle<=-HALF_PI$1&&endAngle>=-HALF_PI$1)||endAngle>=PI$1+HALF_PI$1;
			varminX=contains180?-1:Math.min(startX,startX*cutout,endX,endX*cutout);
			varminY=contains270?-1:Math.min(startY,startY*cutout,endY,endY*cutout);
			varmaxX=contains0?1:Math.max(startX,startX*cutout,endX,endX*cutout);
			varmaxY=contains90?1:Math.max(startY,startY*cutout,endY,endY*cutout);
			ratioX=(maxX-minX)/2;
			ratioY=(maxY-minY)/2;
			offsetX=-(maxX+minX)/2;
			offsetY=-(maxY+minY)/2;
		}

		for(i=0,ilen=arcs.length;i<ilen;++i){
			arcs[i]._options=me._resolveDataElementOptions(arcs[i],i);
		}

		chart.borderWidth=me.getMaxBorderWidth();
		maxWidth=(chartArea.right-chartArea.left-chart.borderWidth)/ratioX;
		maxHeight=(chartArea.bottom-chartArea.top-chart.borderWidth)/ratioY;
		chart.outerRadius=Math.max(Math.min(maxWidth,maxHeight)/2,0);
		chart.innerRadius=Math.max(chart.outerRadius*cutout,0);
		chart.radiusLength=(chart.outerRadius-chart.innerRadius)/(me._getVisibleDatasetWeightTotal()||1);
		chart.offsetX=offsetX*chart.outerRadius;
		chart.offsetY=offsetY*chart.outerRadius;

		meta.total=me.calculateTotal();

		me.outerRadius=chart.outerRadius-chart.radiusLength*me._getRingWeightOffset(me.index);
		me.innerRadius=Math.max(me.outerRadius-chart.radiusLength*chartWeight,0);

		for(i=0,ilen=arcs.length;i<ilen;++i){
			me.updateElement(arcs[i],i,reset);
		}
	},

	updateElement:function(arc,index,reset){
		varme=this;
		varchart=me.chart;
		varchartArea=chart.chartArea;
		varopts=chart.options;
		varanimationOpts=opts.animation;
		varcenterX=(chartArea.left+chartArea.right)/2;
		varcenterY=(chartArea.top+chartArea.bottom)/2;
		varstartAngle=opts.rotation;//nonresetcasehandledlater
		varendAngle=opts.rotation;//nonresetcasehandledlater
		vardataset=me.getDataset();
		varcircumference=reset&&animationOpts.animateRotate?0:arc.hidden?0:me.calculateCircumference(dataset.data[index])*(opts.circumference/DOUBLE_PI$1);
		varinnerRadius=reset&&animationOpts.animateScale?0:me.innerRadius;
		varouterRadius=reset&&animationOpts.animateScale?0:me.outerRadius;
		varoptions=arc._options||{};

		helpers$1.extend(arc,{
			//Utility
			_datasetIndex:me.index,
			_index:index,

			//Desiredviewproperties
			_model:{
				backgroundColor:options.backgroundColor,
				borderColor:options.borderColor,
				borderWidth:options.borderWidth,
				borderAlign:options.borderAlign,
				x:centerX+chart.offsetX,
				y:centerY+chart.offsetY,
				startAngle:startAngle,
				endAngle:endAngle,
				circumference:circumference,
				outerRadius:outerRadius,
				innerRadius:innerRadius,
				label:helpers$1.valueAtIndexOrDefault(dataset.label,index,chart.data.labels[index])
			}
		});

		varmodel=arc._model;

		//Setcorrectanglesifnotresetting
		if(!reset||!animationOpts.animateRotate){
			if(index===0){
				model.startAngle=opts.rotation;
			}else{
				model.startAngle=me.getMeta().data[index-1]._model.endAngle;
			}

			model.endAngle=model.startAngle+model.circumference;
		}

		arc.pivot();
	},

	calculateTotal:function(){
		vardataset=this.getDataset();
		varmeta=this.getMeta();
		vartotal=0;
		varvalue;

		helpers$1.each(meta.data,function(element,index){
			value=dataset.data[index];
			if(!isNaN(value)&&!element.hidden){
				total+=Math.abs(value);
			}
		});

		/*if(total===0){
			total=NaN;
		}*/

		returntotal;
	},

	calculateCircumference:function(value){
		vartotal=this.getMeta().total;
		if(total>0&&!isNaN(value)){
			returnDOUBLE_PI$1*(Math.abs(value)/total);
		}
		return0;
	},

	//getsthemaxborderorhoverwidthtoproperlyscalepiecharts
	getMaxBorderWidth:function(arcs){
		varme=this;
		varmax=0;
		varchart=me.chart;
		vari,ilen,meta,arc,controller,options,borderWidth,hoverWidth;

		if(!arcs){
			//Findtheoutmostvisibledataset
			for(i=0,ilen=chart.data.datasets.length;i<ilen;++i){
				if(chart.isDatasetVisible(i)){
					meta=chart.getDatasetMeta(i);
					arcs=meta.data;
					if(i!==me.index){
						controller=meta.controller;
					}
					break;
				}
			}
		}

		if(!arcs){
			return0;
		}

		for(i=0,ilen=arcs.length;i<ilen;++i){
			arc=arcs[i];
			if(controller){
				controller._configure();
				options=controller._resolveDataElementOptions(arc,i);
			}else{
				options=arc._options;
			}
			if(options.borderAlign!=='inner'){
				borderWidth=options.borderWidth;
				hoverWidth=options.hoverBorderWidth;

				max=borderWidth>max?borderWidth:max;
				max=hoverWidth>max?hoverWidth:max;
			}
		}
		returnmax;
	},

	/**
	*@protected
	*/
	setHoverStyle:function(arc){
		varmodel=arc._model;
		varoptions=arc._options;
		vargetHoverColor=helpers$1.getHoverColor;

		arc.$previousStyle={
			backgroundColor:model.backgroundColor,
			borderColor:model.borderColor,
			borderWidth:model.borderWidth,
		};

		model.backgroundColor=valueOrDefault$5(options.hoverBackgroundColor,getHoverColor(options.backgroundColor));
		model.borderColor=valueOrDefault$5(options.hoverBorderColor,getHoverColor(options.borderColor));
		model.borderWidth=valueOrDefault$5(options.hoverBorderWidth,options.borderWidth);
	},

	/**
	*Getradiuslengthoffsetofthedatasetinrelationtothevisibledatasetsweights.Thisallowsdeterminingtheinnerandouterradiuscorrectly
	*@private
	*/
	_getRingWeightOffset:function(datasetIndex){
		varringWeightOffset=0;

		for(vari=0;i<datasetIndex;++i){
			if(this.chart.isDatasetVisible(i)){
				ringWeightOffset+=this._getRingWeight(i);
			}
		}

		returnringWeightOffset;
	},

	/**
	*@private
	*/
	_getRingWeight:function(dataSetIndex){
		returnMath.max(valueOrDefault$5(this.chart.data.datasets[dataSetIndex].weight,1),0);
	},

	/**
	*Returnsthesumofallvisibiledatasetweights. Thisvaluecanbe0.
	*@private
	*/
	_getVisibleDatasetWeightTotal:function(){
		returnthis._getRingWeightOffset(this.chart.data.datasets.length);
	}
});

core_defaults._set('horizontalBar',{
	hover:{
		mode:'index',
		axis:'y'
	},

	scales:{
		xAxes:[{
			type:'linear',
			position:'bottom'
		}],

		yAxes:[{
			type:'category',
			position:'left',
			offset:true,
			gridLines:{
				offsetGridLines:true
			}
		}]
	},

	elements:{
		rectangle:{
			borderSkipped:'left'
		}
	},

	tooltips:{
		mode:'index',
		axis:'y'
	}
});

core_defaults._set('global',{
	datasets:{
		horizontalBar:{
			categoryPercentage:0.8,
			barPercentage:0.9
		}
	}
});

varcontroller_horizontalBar=controller_bar.extend({
	/**
	*@private
	*/
	_getValueScaleId:function(){
		returnthis.getMeta().xAxisID;
	},

	/**
	*@private
	*/
	_getIndexScaleId:function(){
		returnthis.getMeta().yAxisID;
	}
});

varvalueOrDefault$6=helpers$1.valueOrDefault;
varresolve$2=helpers$1.options.resolve;
varisPointInArea=helpers$1.canvas._isPointInArea;

core_defaults._set('line',{
	showLines:true,
	spanGaps:false,

	hover:{
		mode:'label'
	},

	scales:{
		xAxes:[{
			type:'category',
			id:'x-axis-0'
		}],
		yAxes:[{
			type:'linear',
			id:'y-axis-0'
		}]
	}
});

functionscaleClip(scale,halfBorderWidth){
	vartickOpts=scale&&scale.options.ticks||{};
	varreverse=tickOpts.reverse;
	varmin=tickOpts.min===undefined?halfBorderWidth:0;
	varmax=tickOpts.max===undefined?halfBorderWidth:0;
	return{
		start:reverse?max:min,
		end:reverse?min:max
	};
}

functiondefaultClip(xScale,yScale,borderWidth){
	varhalfBorderWidth=borderWidth/2;
	varx=scaleClip(xScale,halfBorderWidth);
	vary=scaleClip(yScale,halfBorderWidth);

	return{
		top:y.end,
		right:x.end,
		bottom:y.start,
		left:x.start
	};
}

functiontoClip(value){
	vart,r,b,l;

	if(helpers$1.isObject(value)){
		t=value.top;
		r=value.right;
		b=value.bottom;
		l=value.left;
	}else{
		t=r=b=l=value;
	}

	return{
		top:t,
		right:r,
		bottom:b,
		left:l
	};
}


varcontroller_line=core_datasetController.extend({

	datasetElementType:elements.Line,

	dataElementType:elements.Point,

	/**
	*@private
	*/
	_datasetElementOptions:[
		'backgroundColor',
		'borderCapStyle',
		'borderColor',
		'borderDash',
		'borderDashOffset',
		'borderJoinStyle',
		'borderWidth',
		'cubicInterpolationMode',
		'fill'
	],

	/**
	*@private
	*/
	_dataElementOptions:{
		backgroundColor:'pointBackgroundColor',
		borderColor:'pointBorderColor',
		borderWidth:'pointBorderWidth',
		hitRadius:'pointHitRadius',
		hoverBackgroundColor:'pointHoverBackgroundColor',
		hoverBorderColor:'pointHoverBorderColor',
		hoverBorderWidth:'pointHoverBorderWidth',
		hoverRadius:'pointHoverRadius',
		pointStyle:'pointStyle',
		radius:'pointRadius',
		rotation:'pointRotation'
	},

	update:function(reset){
		varme=this;
		varmeta=me.getMeta();
		varline=meta.dataset;
		varpoints=meta.data||[];
		varoptions=me.chart.options;
		varconfig=me._config;
		varshowLine=me._showLine=valueOrDefault$6(config.showLine,options.showLines);
		vari,ilen;

		me._xScale=me.getScaleForId(meta.xAxisID);
		me._yScale=me.getScaleForId(meta.yAxisID);

		//UpdateLine
		if(showLine){
			//Compatibility:Ifthepropertiesaredefinedwithonlytheoldname,usethosevalues
			if(config.tension!==undefined&&config.lineTension===undefined){
				config.lineTension=config.tension;
			}

			//Utility
			line._scale=me._yScale;
			line._datasetIndex=me.index;
			//Data
			line._children=points;
			//Model
			line._model=me._resolveDatasetElementOptions(line);

			line.pivot();
		}

		//UpdatePoints
		for(i=0,ilen=points.length;i<ilen;++i){
			me.updateElement(points[i],i,reset);
		}

		if(showLine&&line._model.tension!==0){
			me.updateBezierControlPoints();
		}

		//Nowpivotthepointforanimation
		for(i=0,ilen=points.length;i<ilen;++i){
			points[i].pivot();
		}
	},

	updateElement:function(point,index,reset){
		varme=this;
		varmeta=me.getMeta();
		varcustom=point.custom||{};
		vardataset=me.getDataset();
		vardatasetIndex=me.index;
		varvalue=dataset.data[index];
		varxScale=me._xScale;
		varyScale=me._yScale;
		varlineModel=meta.dataset._model;
		varx,y;

		varoptions=me._resolveDataElementOptions(point,index);

		x=xScale.getPixelForValue(typeofvalue==='object'?value:NaN,index,datasetIndex);
		y=reset?yScale.getBasePixel():me.calculatePointY(value,index,datasetIndex);

		//Utility
		point._xScale=xScale;
		point._yScale=yScale;
		point._options=options;
		point._datasetIndex=datasetIndex;
		point._index=index;

		//Desiredviewproperties
		point._model={
			x:x,
			y:y,
			skip:custom.skip||isNaN(x)||isNaN(y),
			//Appearance
			radius:options.radius,
			pointStyle:options.pointStyle,
			rotation:options.rotation,
			backgroundColor:options.backgroundColor,
			borderColor:options.borderColor,
			borderWidth:options.borderWidth,
			tension:valueOrDefault$6(custom.tension,lineModel?lineModel.tension:0),
			steppedLine:lineModel?lineModel.steppedLine:false,
			//Tooltip
			hitRadius:options.hitRadius
		};
	},

	/**
	*@private
	*/
	_resolveDatasetElementOptions:function(element){
		varme=this;
		varconfig=me._config;
		varcustom=element.custom||{};
		varoptions=me.chart.options;
		varlineOptions=options.elements.line;
		varvalues=core_datasetController.prototype._resolveDatasetElementOptions.apply(me,arguments);

		//Thedefaultbehavioroflinesistobreakatnullvalues,according
		//tohttps://github.com/chartjs/Chart.js/issues/2435#issuecomment-216718158
		//Thisoptiongiveslinestheabilitytospangaps
		values.spanGaps=valueOrDefault$6(config.spanGaps,options.spanGaps);
		values.tension=valueOrDefault$6(config.lineTension,lineOptions.tension);
		values.steppedLine=resolve$2([custom.steppedLine,config.steppedLine,lineOptions.stepped]);
		values.clip=toClip(valueOrDefault$6(config.clip,defaultClip(me._xScale,me._yScale,values.borderWidth)));

		returnvalues;
	},

	calculatePointY:function(value,index,datasetIndex){
		varme=this;
		varchart=me.chart;
		varyScale=me._yScale;
		varsumPos=0;
		varsumNeg=0;
		vari,ds,dsMeta,stackedRightValue,rightValue,metasets,ilen;

		if(yScale.options.stacked){
			rightValue=+yScale.getRightValue(value);
			metasets=chart._getSortedVisibleDatasetMetas();
			ilen=metasets.length;

			for(i=0;i<ilen;++i){
				dsMeta=metasets[i];
				if(dsMeta.index===datasetIndex){
					break;
				}

				ds=chart.data.datasets[dsMeta.index];
				if(dsMeta.type==='line'&&dsMeta.yAxisID===yScale.id){
					stackedRightValue=+yScale.getRightValue(ds.data[index]);
					if(stackedRightValue<0){
						sumNeg+=stackedRightValue||0;
					}else{
						sumPos+=stackedRightValue||0;
					}
				}
			}

			if(rightValue<0){
				returnyScale.getPixelForValue(sumNeg+rightValue);
			}
			returnyScale.getPixelForValue(sumPos+rightValue);
		}
		returnyScale.getPixelForValue(value);
	},

	updateBezierControlPoints:function(){
		varme=this;
		varchart=me.chart;
		varmeta=me.getMeta();
		varlineModel=meta.dataset._model;
		vararea=chart.chartArea;
		varpoints=meta.data||[];
		vari,ilen,model,controlPoints;

		//OnlyconsiderpointsthataredrawnincasethespanGapsoptionisused
		if(lineModel.spanGaps){
			points=points.filter(function(pt){
				return!pt._model.skip;
			});
		}

		functioncapControlPoint(pt,min,max){
			returnMath.max(Math.min(pt,max),min);
		}

		if(lineModel.cubicInterpolationMode==='monotone'){
			helpers$1.splineCurveMonotone(points);
		}else{
			for(i=0,ilen=points.length;i<ilen;++i){
				model=points[i]._model;
				controlPoints=helpers$1.splineCurve(
					helpers$1.previousItem(points,i)._model,
					model,
					helpers$1.nextItem(points,i)._model,
					lineModel.tension
				);
				model.controlPointPreviousX=controlPoints.previous.x;
				model.controlPointPreviousY=controlPoints.previous.y;
				model.controlPointNextX=controlPoints.next.x;
				model.controlPointNextY=controlPoints.next.y;
			}
		}

		if(chart.options.elements.line.capBezierPoints){
			for(i=0,ilen=points.length;i<ilen;++i){
				model=points[i]._model;
				if(isPointInArea(model,area)){
					if(i>0&&isPointInArea(points[i-1]._model,area)){
						model.controlPointPreviousX=capControlPoint(model.controlPointPreviousX,area.left,area.right);
						model.controlPointPreviousY=capControlPoint(model.controlPointPreviousY,area.top,area.bottom);
					}
					if(i<points.length-1&&isPointInArea(points[i+1]._model,area)){
						model.controlPointNextX=capControlPoint(model.controlPointNextX,area.left,area.right);
						model.controlPointNextY=capControlPoint(model.controlPointNextY,area.top,area.bottom);
					}
				}
			}
		}
	},

	draw:function(){
		varme=this;
		varchart=me.chart;
		varmeta=me.getMeta();
		varpoints=meta.data||[];
		vararea=chart.chartArea;
		varcanvas=chart.canvas;
		vari=0;
		varilen=points.length;
		varclip;

		if(me._showLine){
			clip=meta.dataset._model.clip;

			helpers$1.canvas.clipArea(chart.ctx,{
				left:clip.left===false?0:area.left-clip.left,
				right:clip.right===false?canvas.width:area.right+clip.right,
				top:clip.top===false?0:area.top-clip.top,
				bottom:clip.bottom===false?canvas.height:area.bottom+clip.bottom
			});

			meta.dataset.draw();

			helpers$1.canvas.unclipArea(chart.ctx);
		}

		//Drawthepoints
		for(;i<ilen;++i){
			points[i].draw(area);
		}
	},

	/**
	*@protected
	*/
	setHoverStyle:function(point){
		varmodel=point._model;
		varoptions=point._options;
		vargetHoverColor=helpers$1.getHoverColor;

		point.$previousStyle={
			backgroundColor:model.backgroundColor,
			borderColor:model.borderColor,
			borderWidth:model.borderWidth,
			radius:model.radius
		};

		model.backgroundColor=valueOrDefault$6(options.hoverBackgroundColor,getHoverColor(options.backgroundColor));
		model.borderColor=valueOrDefault$6(options.hoverBorderColor,getHoverColor(options.borderColor));
		model.borderWidth=valueOrDefault$6(options.hoverBorderWidth,options.borderWidth);
		model.radius=valueOrDefault$6(options.hoverRadius,options.radius);
	},
});

varresolve$3=helpers$1.options.resolve;

core_defaults._set('polarArea',{
	scale:{
		type:'radialLinear',
		angleLines:{
			display:false
		},
		gridLines:{
			circular:true
		},
		pointLabels:{
			display:false
		},
		ticks:{
			beginAtZero:true
		}
	},

	//Boolean-Whethertoanimatetherotationofthechart
	animation:{
		animateRotate:true,
		animateScale:true
	},

	startAngle:-0.5*Math.PI,
	legendCallback:function(chart){
		varlist=document.createElement('ul');
		vardata=chart.data;
		vardatasets=data.datasets;
		varlabels=data.labels;
		vari,ilen,listItem,listItemSpan;

		list.setAttribute('class',chart.id+'-legend');
		if(datasets.length){
			for(i=0,ilen=datasets[0].data.length;i<ilen;++i){
				listItem=list.appendChild(document.createElement('li'));
				listItemSpan=listItem.appendChild(document.createElement('span'));
				listItemSpan.style.backgroundColor=datasets[0].backgroundColor[i];
				if(labels[i]){
					listItem.appendChild(document.createTextNode(labels[i]));
				}
			}
		}

		returnlist.outerHTML;
	},
	legend:{
		labels:{
			generateLabels:function(chart){
				vardata=chart.data;
				if(data.labels.length&&data.datasets.length){
					returndata.labels.map(function(label,i){
						varmeta=chart.getDatasetMeta(0);
						varstyle=meta.controller.getStyle(i);

						return{
							text:label,
							fillStyle:style.backgroundColor,
							strokeStyle:style.borderColor,
							lineWidth:style.borderWidth,
							hidden:isNaN(data.datasets[0].data[i])||meta.data[i].hidden,

							//Extradatausedfortogglingthecorrectitem
							index:i
						};
					});
				}
				return[];
			}
		},

		onClick:function(e,legendItem){
			varindex=legendItem.index;
			varchart=this.chart;
			vari,ilen,meta;

			for(i=0,ilen=(chart.data.datasets||[]).length;i<ilen;++i){
				meta=chart.getDatasetMeta(i);
				meta.data[index].hidden=!meta.data[index].hidden;
			}

			chart.update();
		}
	},

	//Needtooverridethesetogiveanicedefault
	tooltips:{
		callbacks:{
			title:function(){
				return'';
			},
			label:function(item,data){
				returndata.labels[item.index]+':'+item.yLabel;
			}
		}
	}
});

varcontroller_polarArea=core_datasetController.extend({

	dataElementType:elements.Arc,

	linkScales:helpers$1.noop,

	/**
	*@private
	*/
	_dataElementOptions:[
		'backgroundColor',
		'borderColor',
		'borderWidth',
		'borderAlign',
		'hoverBackgroundColor',
		'hoverBorderColor',
		'hoverBorderWidth',
	],

	/**
	*@private
	*/
	_getIndexScaleId:function(){
		returnthis.chart.scale.id;
	},

	/**
	*@private
	*/
	_getValueScaleId:function(){
		returnthis.chart.scale.id;
	},

	update:function(reset){
		varme=this;
		vardataset=me.getDataset();
		varmeta=me.getMeta();
		varstart=me.chart.options.startAngle||0;
		varstarts=me._starts=[];
		varangles=me._angles=[];
		vararcs=meta.data;
		vari,ilen,angle;

		me._updateRadius();

		meta.count=me.countVisibleElements();

		for(i=0,ilen=dataset.data.length;i<ilen;i++){
			starts[i]=start;
			angle=me._computeAngle(i);
			angles[i]=angle;
			start+=angle;
		}

		for(i=0,ilen=arcs.length;i<ilen;++i){
			arcs[i]._options=me._resolveDataElementOptions(arcs[i],i);
			me.updateElement(arcs[i],i,reset);
		}
	},

	/**
	*@private
	*/
	_updateRadius:function(){
		varme=this;
		varchart=me.chart;
		varchartArea=chart.chartArea;
		varopts=chart.options;
		varminSize=Math.min(chartArea.right-chartArea.left,chartArea.bottom-chartArea.top);

		chart.outerRadius=Math.max(minSize/2,0);
		chart.innerRadius=Math.max(opts.cutoutPercentage?(chart.outerRadius/100)*(opts.cutoutPercentage):1,0);
		chart.radiusLength=(chart.outerRadius-chart.innerRadius)/chart.getVisibleDatasetCount();

		me.outerRadius=chart.outerRadius-(chart.radiusLength*me.index);
		me.innerRadius=me.outerRadius-chart.radiusLength;
	},

	updateElement:function(arc,index,reset){
		varme=this;
		varchart=me.chart;
		vardataset=me.getDataset();
		varopts=chart.options;
		varanimationOpts=opts.animation;
		varscale=chart.scale;
		varlabels=chart.data.labels;

		varcenterX=scale.xCenter;
		varcenterY=scale.yCenter;

		//varnegHalfPI=-0.5*Math.PI;
		vardatasetStartAngle=opts.startAngle;
		vardistance=arc.hidden?0:scale.getDistanceFromCenterForValue(dataset.data[index]);
		varstartAngle=me._starts[index];
		varendAngle=startAngle+(arc.hidden?0:me._angles[index]);

		varresetRadius=animationOpts.animateScale?0:scale.getDistanceFromCenterForValue(dataset.data[index]);
		varoptions=arc._options||{};

		helpers$1.extend(arc,{
			//Utility
			_datasetIndex:me.index,
			_index:index,
			_scale:scale,

			//Desiredviewproperties
			_model:{
				backgroundColor:options.backgroundColor,
				borderColor:options.borderColor,
				borderWidth:options.borderWidth,
				borderAlign:options.borderAlign,
				x:centerX,
				y:centerY,
				innerRadius:0,
				outerRadius:reset?resetRadius:distance,
				startAngle:reset&&animationOpts.animateRotate?datasetStartAngle:startAngle,
				endAngle:reset&&animationOpts.animateRotate?datasetStartAngle:endAngle,
				label:helpers$1.valueAtIndexOrDefault(labels,index,labels[index])
			}
		});

		arc.pivot();
	},

	countVisibleElements:function(){
		vardataset=this.getDataset();
		varmeta=this.getMeta();
		varcount=0;

		helpers$1.each(meta.data,function(element,index){
			if(!isNaN(dataset.data[index])&&!element.hidden){
				count++;
			}
		});

		returncount;
	},

	/**
	*@protected
	*/
	setHoverStyle:function(arc){
		varmodel=arc._model;
		varoptions=arc._options;
		vargetHoverColor=helpers$1.getHoverColor;
		varvalueOrDefault=helpers$1.valueOrDefault;

		arc.$previousStyle={
			backgroundColor:model.backgroundColor,
			borderColor:model.borderColor,
			borderWidth:model.borderWidth,
		};

		model.backgroundColor=valueOrDefault(options.hoverBackgroundColor,getHoverColor(options.backgroundColor));
		model.borderColor=valueOrDefault(options.hoverBorderColor,getHoverColor(options.borderColor));
		model.borderWidth=valueOrDefault(options.hoverBorderWidth,options.borderWidth);
	},

	/**
	*@private
	*/
	_computeAngle:function(index){
		varme=this;
		varcount=this.getMeta().count;
		vardataset=me.getDataset();
		varmeta=me.getMeta();

		if(isNaN(dataset.data[index])||meta.data[index].hidden){
			return0;
		}

		//Scriptableoptions
		varcontext={
			chart:me.chart,
			dataIndex:index,
			dataset:dataset,
			datasetIndex:me.index
		};

		returnresolve$3([
			me.chart.options.elements.arc.angle,
			(2*Math.PI)/count
		],context,index);
	}
});

core_defaults._set('pie',helpers$1.clone(core_defaults.doughnut));
core_defaults._set('pie',{
	cutoutPercentage:0
});

//PiechartsareDoughnutchartwithdifferentdefaults
varcontroller_pie=controller_doughnut;

varvalueOrDefault$7=helpers$1.valueOrDefault;

core_defaults._set('radar',{
	spanGaps:false,
	scale:{
		type:'radialLinear'
	},
	elements:{
		line:{
			fill:'start',
			tension:0//nobezierinradar
		}
	}
});

varcontroller_radar=core_datasetController.extend({
	datasetElementType:elements.Line,

	dataElementType:elements.Point,

	linkScales:helpers$1.noop,

	/**
	*@private
	*/
	_datasetElementOptions:[
		'backgroundColor',
		'borderWidth',
		'borderColor',
		'borderCapStyle',
		'borderDash',
		'borderDashOffset',
		'borderJoinStyle',
		'fill'
	],

	/**
	*@private
	*/
	_dataElementOptions:{
		backgroundColor:'pointBackgroundColor',
		borderColor:'pointBorderColor',
		borderWidth:'pointBorderWidth',
		hitRadius:'pointHitRadius',
		hoverBackgroundColor:'pointHoverBackgroundColor',
		hoverBorderColor:'pointHoverBorderColor',
		hoverBorderWidth:'pointHoverBorderWidth',
		hoverRadius:'pointHoverRadius',
		pointStyle:'pointStyle',
		radius:'pointRadius',
		rotation:'pointRotation'
	},

	/**
	*@private
	*/
	_getIndexScaleId:function(){
		returnthis.chart.scale.id;
	},

	/**
	*@private
	*/
	_getValueScaleId:function(){
		returnthis.chart.scale.id;
	},

	update:function(reset){
		varme=this;
		varmeta=me.getMeta();
		varline=meta.dataset;
		varpoints=meta.data||[];
		varscale=me.chart.scale;
		varconfig=me._config;
		vari,ilen;

		//Compatibility:Ifthepropertiesaredefinedwithonlytheoldname,usethosevalues
		if(config.tension!==undefined&&config.lineTension===undefined){
			config.lineTension=config.tension;
		}

		//Utility
		line._scale=scale;
		line._datasetIndex=me.index;
		//Data
		line._children=points;
		line._loop=true;
		//Model
		line._model=me._resolveDatasetElementOptions(line);

		line.pivot();

		//UpdatePoints
		for(i=0,ilen=points.length;i<ilen;++i){
			me.updateElement(points[i],i,reset);
		}

		//Updatebeziercontrolpoints
		me.updateBezierControlPoints();

		//Nowpivotthepointforanimation
		for(i=0,ilen=points.length;i<ilen;++i){
			points[i].pivot();
		}
	},

	updateElement:function(point,index,reset){
		varme=this;
		varcustom=point.custom||{};
		vardataset=me.getDataset();
		varscale=me.chart.scale;
		varpointPosition=scale.getPointPositionForValue(index,dataset.data[index]);
		varoptions=me._resolveDataElementOptions(point,index);
		varlineModel=me.getMeta().dataset._model;
		varx=reset?scale.xCenter:pointPosition.x;
		vary=reset?scale.yCenter:pointPosition.y;

		//Utility
		point._scale=scale;
		point._options=options;
		point._datasetIndex=me.index;
		point._index=index;

		//Desiredviewproperties
		point._model={
			x:x,//valuenotusedindatasetscale,butwewantaconsistentAPIbetweenscales
			y:y,
			skip:custom.skip||isNaN(x)||isNaN(y),
			//Appearance
			radius:options.radius,
			pointStyle:options.pointStyle,
			rotation:options.rotation,
			backgroundColor:options.backgroundColor,
			borderColor:options.borderColor,
			borderWidth:options.borderWidth,
			tension:valueOrDefault$7(custom.tension,lineModel?lineModel.tension:0),

			//Tooltip
			hitRadius:options.hitRadius
		};
	},

	/**
	*@private
	*/
	_resolveDatasetElementOptions:function(){
		varme=this;
		varconfig=me._config;
		varoptions=me.chart.options;
		varvalues=core_datasetController.prototype._resolveDatasetElementOptions.apply(me,arguments);

		values.spanGaps=valueOrDefault$7(config.spanGaps,options.spanGaps);
		values.tension=valueOrDefault$7(config.lineTension,options.elements.line.tension);

		returnvalues;
	},

	updateBezierControlPoints:function(){
		varme=this;
		varmeta=me.getMeta();
		vararea=me.chart.chartArea;
		varpoints=meta.data||[];
		vari,ilen,model,controlPoints;

		//OnlyconsiderpointsthataredrawnincasethespanGapsoptionisused
		if(meta.dataset._model.spanGaps){
			points=points.filter(function(pt){
				return!pt._model.skip;
			});
		}

		functioncapControlPoint(pt,min,max){
			returnMath.max(Math.min(pt,max),min);
		}

		for(i=0,ilen=points.length;i<ilen;++i){
			model=points[i]._model;
			controlPoints=helpers$1.splineCurve(
				helpers$1.previousItem(points,i,true)._model,
				model,
				helpers$1.nextItem(points,i,true)._model,
				model.tension
			);

			//Preventthebeziergoingoutsideoftheboundsofthegraph
			model.controlPointPreviousX=capControlPoint(controlPoints.previous.x,area.left,area.right);
			model.controlPointPreviousY=capControlPoint(controlPoints.previous.y,area.top,area.bottom);
			model.controlPointNextX=capControlPoint(controlPoints.next.x,area.left,area.right);
			model.controlPointNextY=capControlPoint(controlPoints.next.y,area.top,area.bottom);
		}
	},

	setHoverStyle:function(point){
		varmodel=point._model;
		varoptions=point._options;
		vargetHoverColor=helpers$1.getHoverColor;

		point.$previousStyle={
			backgroundColor:model.backgroundColor,
			borderColor:model.borderColor,
			borderWidth:model.borderWidth,
			radius:model.radius
		};

		model.backgroundColor=valueOrDefault$7(options.hoverBackgroundColor,getHoverColor(options.backgroundColor));
		model.borderColor=valueOrDefault$7(options.hoverBorderColor,getHoverColor(options.borderColor));
		model.borderWidth=valueOrDefault$7(options.hoverBorderWidth,options.borderWidth);
		model.radius=valueOrDefault$7(options.hoverRadius,options.radius);
	}
});

core_defaults._set('scatter',{
	hover:{
		mode:'single'
	},

	scales:{
		xAxes:[{
			id:'x-axis-1',   //needanIDsodatasetscanreferencethescale
			type:'linear',   //scattershouldnotuseacategoryaxis
			position:'bottom'
		}],
		yAxes:[{
			id:'y-axis-1',
			type:'linear',
			position:'left'
		}]
	},

	tooltips:{
		callbacks:{
			title:function(){
				return'';    //doesn'tmakesenseforscattersincedataareformattedasapoint
			},
			label:function(item){
				return'('+item.xLabel+','+item.yLabel+')';
			}
		}
	}
});

core_defaults._set('global',{
	datasets:{
		scatter:{
			showLine:false
		}
	}
});

//Scatterchartsuselinecontrollers
varcontroller_scatter=controller_line;

//NOTEexportamapinwhichthekeyrepresentsthecontrollertype,not
//theclass,andsomustbeCamelCaseinordertobecorrectlyretrieved
//bythecontrollerincore.controller.js(`controllers[meta.type]`).

varcontrollers={
	bar:controller_bar,
	bubble:controller_bubble,
	doughnut:controller_doughnut,
	horizontalBar:controller_horizontalBar,
	line:controller_line,
	polarArea:controller_polarArea,
	pie:controller_pie,
	radar:controller_radar,
	scatter:controller_scatter
};

/**
 *Helperfunctiontogetrelativepositionforanevent
 *@param{Event|IEvent}event-Theeventtogetthepositionfor
 *@param{Chart}chart-Thechart
 *@returns{object}theeventposition
 */
functiongetRelativePosition(e,chart){
	if(e.native){
		return{
			x:e.x,
			y:e.y
		};
	}

	returnhelpers$1.getRelativePosition(e,chart);
}

/**
 *Helperfunctiontotraverseallofthevisibleelementsinthechart
 *@param{Chart}chart-thechart
 *@param{function}handler-thecallbacktoexecuteforeachvisibleitem
 */
functionparseVisibleItems(chart,handler){
	varmetasets=chart._getSortedVisibleDatasetMetas();
	varmetadata,i,j,ilen,jlen,element;

	for(i=0,ilen=metasets.length;i<ilen;++i){
		metadata=metasets[i].data;
		for(j=0,jlen=metadata.length;j<jlen;++j){
			element=metadata[j];
			if(!element._view.skip){
				handler(element);
			}
		}
	}
}

/**
 *Helperfunctiontogettheitemsthatintersecttheeventposition
 *@param{ChartElement[]}items-elementstofilter
 *@param{object}position-thepointtobenearestto
 *@return{ChartElement[]}thenearestitems
 */
functiongetIntersectItems(chart,position){
	varelements=[];

	parseVisibleItems(chart,function(element){
		if(element.inRange(position.x,position.y)){
			elements.push(element);
		}
	});

	returnelements;
}

/**
 *Helperfunctiontogettheitemsnearesttotheeventpositionconsideringallvisibleitemsintehchart
 *@param{Chart}chart-thecharttolookatelementsfrom
 *@param{object}position-thepointtobenearestto
 *@param{boolean}intersect-iftrue,onlyconsideritemsthatintersecttheposition
 *@param{function}distanceMetric-functiontoprovidethedistancebetweenpoints
 *@return{ChartElement[]}thenearestitems
 */
functiongetNearestItems(chart,position,intersect,distanceMetric){
	varminDistance=Number.POSITIVE_INFINITY;
	varnearestItems=[];

	parseVisibleItems(chart,function(element){
		if(intersect&&!element.inRange(position.x,position.y)){
			return;
		}

		varcenter=element.getCenterPoint();
		vardistance=distanceMetric(position,center);
		if(distance<minDistance){
			nearestItems=[element];
			minDistance=distance;
		}elseif(distance===minDistance){
			//Canhavemultipleitemsatthesamedistanceinwhichcasewesortbysize
			nearestItems.push(element);
		}
	});

	returnnearestItems;
}

/**
 *Getadistancemetricfunctionfortwopointsbasedonthe
 *axismodesetting
 *@param{string}axis-theaxismode.x|y|xy
 */
functiongetDistanceMetricForAxis(axis){
	varuseX=axis.indexOf('x')!==-1;
	varuseY=axis.indexOf('y')!==-1;

	returnfunction(pt1,pt2){
		vardeltaX=useX?Math.abs(pt1.x-pt2.x):0;
		vardeltaY=useY?Math.abs(pt1.y-pt2.y):0;
		returnMath.sqrt(Math.pow(deltaX,2)+Math.pow(deltaY,2));
	};
}

functionindexMode(chart,e,options){
	varposition=getRelativePosition(e,chart);
	//Defaultaxisforindexmodeis'x'tomatcholdbehaviour
	options.axis=options.axis||'x';
	vardistanceMetric=getDistanceMetricForAxis(options.axis);
	varitems=options.intersect?getIntersectItems(chart,position):getNearestItems(chart,position,false,distanceMetric);
	varelements=[];

	if(!items.length){
		return[];
	}

	chart._getSortedVisibleDatasetMetas().forEach(function(meta){
		varelement=meta.data[items[0]._index];

		//don'tcountitemsthatareskipped(nulldata)
		if(element&&!element._view.skip){
			elements.push(element);
		}
	});

	returnelements;
}

/**
 *@interfaceIInteractionOptions
 */
/**
 *Iftrue,onlyconsideritemsthatintersectthepoint
 *@nameIInterfaceOptions#boolean
 *@typeBoolean
 */

/**
 *Containsinteractionrelatedfunctions
 *@namespaceChart.Interaction
 */
varcore_interaction={
	//Helperfunctionfordifferentmodes
	modes:{
		single:function(chart,e){
			varposition=getRelativePosition(e,chart);
			varelements=[];

			parseVisibleItems(chart,function(element){
				if(element.inRange(position.x,position.y)){
					elements.push(element);
					returnelements;
				}
			});

			returnelements.slice(0,1);
		},

		/**
		*@functionChart.Interaction.modes.label
		*@deprecatedsinceversion2.4.0
		*@todoremoveatversion3
		*@private
		*/
		label:indexMode,

		/**
		*Returnsitemsatthesameindex.Iftheoptions.intersectparameteristrue,weonlyreturnitemsifweintersectsomething
		*Iftheoptions.intersectmodeisfalse,wefindthenearestitemandreturntheitemsatthesameindexasthatitem
		*@functionChart.Interaction.modes.index
		*@sincev2.4.0
		*@param{Chart}chart-thechartwearereturningitemsfrom
		*@param{Event}e-theeventwearefindthingsat
		*@param{IInteractionOptions}options-optionstouseduringinteraction
		*@return{Chart.Element[]}Arrayofelementsthatareunderthepoint.Ifnonearefound,anemptyarrayisreturned
		*/
		index:indexMode,

		/**
		*Returnsitemsinthesamedataset.Iftheoptions.intersectparameteristrue,weonlyreturnitemsifweintersectsomething
		*Iftheoptions.intersectisfalse,wefindthenearestitemandreturntheitemsinthatdataset
		*@functionChart.Interaction.modes.dataset
		*@param{Chart}chart-thechartwearereturningitemsfrom
		*@param{Event}e-theeventwearefindthingsat
		*@param{IInteractionOptions}options-optionstouseduringinteraction
		*@return{Chart.Element[]}Arrayofelementsthatareunderthepoint.Ifnonearefound,anemptyarrayisreturned
		*/
		dataset:function(chart,e,options){
			varposition=getRelativePosition(e,chart);
			options.axis=options.axis||'xy';
			vardistanceMetric=getDistanceMetricForAxis(options.axis);
			varitems=options.intersect?getIntersectItems(chart,position):getNearestItems(chart,position,false,distanceMetric);

			if(items.length>0){
				items=chart.getDatasetMeta(items[0]._datasetIndex).data;
			}

			returnitems;
		},

		/**
		*@functionChart.Interaction.modes.x-axis
		*@deprecatedsinceversion2.4.0.Useindexmodeandintersect==true
		*@todoremoveatversion3
		*@private
		*/
		'x-axis':function(chart,e){
			returnindexMode(chart,e,{intersect:false});
		},

		/**
		*Pointmodereturnsallelementsthathittestbasedontheeventposition
		*oftheevent
		*@functionChart.Interaction.modes.intersect
		*@param{Chart}chart-thechartwearereturningitemsfrom
		*@param{Event}e-theeventwearefindthingsat
		*@return{Chart.Element[]}Arrayofelementsthatareunderthepoint.Ifnonearefound,anemptyarrayisreturned
		*/
		point:function(chart,e){
			varposition=getRelativePosition(e,chart);
			returngetIntersectItems(chart,position);
		},

		/**
		*nearestmodereturnstheelementclosesttothepoint
		*@functionChart.Interaction.modes.intersect
		*@param{Chart}chart-thechartwearereturningitemsfrom
		*@param{Event}e-theeventwearefindthingsat
		*@param{IInteractionOptions}options-optionstouse
		*@return{Chart.Element[]}Arrayofelementsthatareunderthepoint.Ifnonearefound,anemptyarrayisreturned
		*/
		nearest:function(chart,e,options){
			varposition=getRelativePosition(e,chart);
			options.axis=options.axis||'xy';
			vardistanceMetric=getDistanceMetricForAxis(options.axis);
			returngetNearestItems(chart,position,options.intersect,distanceMetric);
		},

		/**
		*xmodereturnstheelementsthathit-testatthecurrentxcoordinate
		*@functionChart.Interaction.modes.x
		*@param{Chart}chart-thechartwearereturningitemsfrom
		*@param{Event}e-theeventwearefindthingsat
		*@param{IInteractionOptions}options-optionstouse
		*@return{Chart.Element[]}Arrayofelementsthatareunderthepoint.Ifnonearefound,anemptyarrayisreturned
		*/
		x:function(chart,e,options){
			varposition=getRelativePosition(e,chart);
			varitems=[];
			varintersectsItem=false;

			parseVisibleItems(chart,function(element){
				if(element.inXRange(position.x)){
					items.push(element);
				}

				if(element.inRange(position.x,position.y)){
					intersectsItem=true;
				}
			});

			//Ifwewanttotriggeronanintersectandwedon'thaveanyitems
			//thatintersecttheposition,returnnothing
			if(options.intersect&&!intersectsItem){
				items=[];
			}
			returnitems;
		},

		/**
		*ymodereturnstheelementsthathit-testatthecurrentycoordinate
		*@functionChart.Interaction.modes.y
		*@param{Chart}chart-thechartwearereturningitemsfrom
		*@param{Event}e-theeventwearefindthingsat
		*@param{IInteractionOptions}options-optionstouse
		*@return{Chart.Element[]}Arrayofelementsthatareunderthepoint.Ifnonearefound,anemptyarrayisreturned
		*/
		y:function(chart,e,options){
			varposition=getRelativePosition(e,chart);
			varitems=[];
			varintersectsItem=false;

			parseVisibleItems(chart,function(element){
				if(element.inYRange(position.y)){
					items.push(element);
				}

				if(element.inRange(position.x,position.y)){
					intersectsItem=true;
				}
			});

			//Ifwewanttotriggeronanintersectandwedon'thaveanyitems
			//thatintersecttheposition,returnnothing
			if(options.intersect&&!intersectsItem){
				items=[];
			}
			returnitems;
		}
	}
};

varextend=helpers$1.extend;

functionfilterByPosition(array,position){
	returnhelpers$1.where(array,function(v){
		returnv.pos===position;
	});
}

functionsortByWeight(array,reverse){
	returnarray.sort(function(a,b){
		varv0=reverse?b:a;
		varv1=reverse?a:b;
		returnv0.weight===v1.weight?
			v0.index-v1.index:
			v0.weight-v1.weight;
	});
}

functionwrapBoxes(boxes){
	varlayoutBoxes=[];
	vari,ilen,box;

	for(i=0,ilen=(boxes||[]).length;i<ilen;++i){
		box=boxes[i];
		layoutBoxes.push({
			index:i,
			box:box,
			pos:box.position,
			horizontal:box.isHorizontal(),
			weight:box.weight
		});
	}
	returnlayoutBoxes;
}

functionsetLayoutDims(layouts,params){
	vari,ilen,layout;
	for(i=0,ilen=layouts.length;i<ilen;++i){
		layout=layouts[i];
		//storewidthusedinsteadofchartArea.winfitBoxes
		layout.width=layout.horizontal
			?layout.box.fullWidth&&params.availableWidth
			:params.vBoxMaxWidth;
		//storeheightusedinsteadofchartArea.hinfitBoxes
		layout.height=layout.horizontal&&params.hBoxMaxHeight;
	}
}

functionbuildLayoutBoxes(boxes){
	varlayoutBoxes=wrapBoxes(boxes);
	varleft=sortByWeight(filterByPosition(layoutBoxes,'left'),true);
	varright=sortByWeight(filterByPosition(layoutBoxes,'right'));
	vartop=sortByWeight(filterByPosition(layoutBoxes,'top'),true);
	varbottom=sortByWeight(filterByPosition(layoutBoxes,'bottom'));

	return{
		leftAndTop:left.concat(top),
		rightAndBottom:right.concat(bottom),
		chartArea:filterByPosition(layoutBoxes,'chartArea'),
		vertical:left.concat(right),
		horizontal:top.concat(bottom)
	};
}

functiongetCombinedMax(maxPadding,chartArea,a,b){
	returnMath.max(maxPadding[a],chartArea[a])+Math.max(maxPadding[b],chartArea[b]);
}

functionupdateDims(chartArea,params,layout){
	varbox=layout.box;
	varmaxPadding=chartArea.maxPadding;
	varnewWidth,newHeight;

	if(layout.size){
		//thislayoutwasalreadycountedfor,letsfirstreduceoldsize
		chartArea[layout.pos]-=layout.size;
	}
	layout.size=layout.horizontal?box.height:box.width;
	chartArea[layout.pos]+=layout.size;

	if(box.getPadding){
		varboxPadding=box.getPadding();
		maxPadding.top=Math.max(maxPadding.top,boxPadding.top);
		maxPadding.left=Math.max(maxPadding.left,boxPadding.left);
		maxPadding.bottom=Math.max(maxPadding.bottom,boxPadding.bottom);
		maxPadding.right=Math.max(maxPadding.right,boxPadding.right);
	}

	newWidth=params.outerWidth-getCombinedMax(maxPadding,chartArea,'left','right');
	newHeight=params.outerHeight-getCombinedMax(maxPadding,chartArea,'top','bottom');

	if(newWidth!==chartArea.w||newHeight!==chartArea.h){
		chartArea.w=newWidth;
		chartArea.h=newHeight;

		//returntrueifchartareachangedinlayout'sdirection
		varsizes=layout.horizontal?[newWidth,chartArea.w]:[newHeight,chartArea.h];
		returnsizes[0]!==sizes[1]&&(!isNaN(sizes[0])||!isNaN(sizes[1]));
	}
}

functionhandleMaxPadding(chartArea){
	varmaxPadding=chartArea.maxPadding;

	functionupdatePos(pos){
		varchange=Math.max(maxPadding[pos]-chartArea[pos],0);
		chartArea[pos]+=change;
		returnchange;
	}
	chartArea.y+=updatePos('top');
	chartArea.x+=updatePos('left');
	updatePos('right');
	updatePos('bottom');
}

functiongetMargins(horizontal,chartArea){
	varmaxPadding=chartArea.maxPadding;

	functionmarginForPositions(positions){
		varmargin={left:0,top:0,right:0,bottom:0};
		positions.forEach(function(pos){
			margin[pos]=Math.max(chartArea[pos],maxPadding[pos]);
		});
		returnmargin;
	}

	returnhorizontal
		?marginForPositions(['left','right'])
		:marginForPositions(['top','bottom']);
}

functionfitBoxes(boxes,chartArea,params){
	varrefitBoxes=[];
	vari,ilen,layout,box,refit,changed;

	for(i=0,ilen=boxes.length;i<ilen;++i){
		layout=boxes[i];
		box=layout.box;

		box.update(
			layout.width||chartArea.w,
			layout.height||chartArea.h,
			getMargins(layout.horizontal,chartArea)
		);
		if(updateDims(chartArea,params,layout)){
			changed=true;
			if(refitBoxes.length){
				//Dimensionschangedandtherewerenonfullwidthboxesbeforethis
				//->wehavetorefitthose
				refit=true;
			}
		}
		if(!box.fullWidth){//fullWidthboxesdon'tneedtobere-fittedinanycase
			refitBoxes.push(layout);
		}
	}

	returnrefit?fitBoxes(refitBoxes,chartArea,params)||changed:changed;
}

functionplaceBoxes(boxes,chartArea,params){
	varuserPadding=params.padding;
	varx=chartArea.x;
	vary=chartArea.y;
	vari,ilen,layout,box;

	for(i=0,ilen=boxes.length;i<ilen;++i){
		layout=boxes[i];
		box=layout.box;
		if(layout.horizontal){
			box.left=box.fullWidth?userPadding.left:chartArea.left;
			box.right=box.fullWidth?params.outerWidth-userPadding.right:chartArea.left+chartArea.w;
			box.top=y;
			box.bottom=y+box.height;
			box.width=box.right-box.left;
			y=box.bottom;
		}else{
			box.left=x;
			box.right=x+box.width;
			box.top=chartArea.top;
			box.bottom=chartArea.top+chartArea.h;
			box.height=box.bottom-box.top;
			x=box.right;
		}
	}

	chartArea.x=x;
	chartArea.y=y;
}

core_defaults._set('global',{
	layout:{
		padding:{
			top:0,
			right:0,
			bottom:0,
			left:0
		}
	}
});

/**
 *@interfaceILayoutItem
 *@prop{string}position-Thepositionoftheiteminthechartlayout.Possiblevaluesare
 *'left','top','right','bottom',and'chartArea'
 *@prop{number}weight-Theweightusedtosorttheitem.Higherweightsarefurtherawayfromthechartarea
 *@prop{boolean}fullWidth-iftrue,andtheitemishorizontal,thenpushverticalboxesdown
 *@prop{function}isHorizontal-returnstrueifthelayoutitemishorizontal(ie.toporbottom)
 *@prop{function}update-Takestwoparameters:widthandheight.Returnssizeofitem
 *@prop{function}getPadding- Returnsanobjectwithpaddingontheedges
 *@prop{number}width-Widthofitem.Mustbevalidafterupdate()
 *@prop{number}height-Heightofitem.Mustbevalidafterupdate()
 *@prop{number}left-Leftedgeoftheitem.Setbylayoutsystemandcannotbeusedinupdate
 *@prop{number}top-Topedgeoftheitem.Setbylayoutsystemandcannotbeusedinupdate
 *@prop{number}right-Rightedgeoftheitem.Setbylayoutsystemandcannotbeusedinupdate
 *@prop{number}bottom-Bottomedgeoftheitem.Setbylayoutsystemandcannotbeusedinupdate
 */

//Thelayoutserviceisveryselfexplanatory. It'sresponsibleforthelayoutwithinachart.
//Scales,LegendsandPluginsallrelyonthelayoutserviceandcaneasilyregistertobeplacedanywheretheyneed
//Itisthisservice'sresponsibilityofcarryingoutthatlayout.
varcore_layouts={
	defaults:{},

	/**
	*Registeraboxtoachart.
	*Aboxissimplyareferencetoanobjectthatrequireslayout.eg.Scales,Legend,Title.
	*@param{Chart}chart-thecharttouse
	*@param{ILayoutItem}item-theitemtoaddtobelayedout
	*/
	addBox:function(chart,item){
		if(!chart.boxes){
			chart.boxes=[];
		}

		//initializeitemwithdefaultvalues
		item.fullWidth=item.fullWidth||false;
		item.position=item.position||'top';
		item.weight=item.weight||0;
		item._layers=item._layers||function(){
			return[{
				z:0,
				draw:function(){
					item.draw.apply(item,arguments);
				}
			}];
		};

		chart.boxes.push(item);
	},

	/**
	*RemovealayoutItemfromachart
	*@param{Chart}chart-thecharttoremovetheboxfrom
	*@param{ILayoutItem}layoutItem-theitemtoremovefromthelayout
	*/
	removeBox:function(chart,layoutItem){
		varindex=chart.boxes?chart.boxes.indexOf(layoutItem):-1;
		if(index!==-1){
			chart.boxes.splice(index,1);
		}
	},

	/**
	*Sets(orupdates)optionsonthegiven`item`.
	*@param{Chart}chart-thechartinwhichtheitemlives(orwillbeaddedto)
	*@param{ILayoutItem}item-theitemtoconfigurewiththegivenoptions
	*@param{object}options-thenewitemoptions.
	*/
	configure:function(chart,item,options){
		varprops=['fullWidth','position','weight'];
		varilen=props.length;
		vari=0;
		varprop;

		for(;i<ilen;++i){
			prop=props[i];
			if(options.hasOwnProperty(prop)){
				item[prop]=options[prop];
			}
		}
	},

	/**
	*Fitsboxesofthegivenchartintothegivensizebyhavingeachboxmeasureitself
	*thenrunningafittingalgorithm
	*@param{Chart}chart-thechart
	*@param{number}width-thewidthtofitinto
	*@param{number}height-theheighttofitinto
	*/
	update:function(chart,width,height){
		if(!chart){
			return;
		}

		varlayoutOptions=chart.options.layout||{};
		varpadding=helpers$1.options.toPadding(layoutOptions.padding);

		varavailableWidth=width-padding.width;
		varavailableHeight=height-padding.height;
		varboxes=buildLayoutBoxes(chart.boxes);
		varverticalBoxes=boxes.vertical;
		varhorizontalBoxes=boxes.horizontal;

		//Essentiallywenowhaveanynumberofboxesoneachofthe4sides.
		//Ourcanvaslookslikethefollowing.
		//TheareasL1andL2aretheleftaxes.R1istherightaxis,T1isthetopaxisand
		//B1isthebottomaxis
		//Therearealso4quadrant-likelocations(lefttorightinsteadofclockwise)reservedforchartoverlays
		//Theselocationsaresingle-boxlocationsonly,whentryingtoregisterachartArealocationthatisalreadytaken,
		//anerrorwillbethrown.
		//
		//|----------------------------------------------------|
		//|                 T1(FullWidth)                  |
		//|----------------------------------------------------|
		//|   |   |                T2                 |   |
		//|   |----|-------------------------------------|----|
		//|   |   |C1|                          |C2|   |
		//|   |   |----|                          |----|   |
		//|   |   |                                    |   |
		//|L1|L2|          ChartArea(C0)           |R1|
		//|   |   |                                    |   |
		//|   |   |----|                          |----|   |
		//|   |   |C3|                          |C4|   |
		//|   |----|-------------------------------------|----|
		//|   |   |                B1                 |   |
		//|----------------------------------------------------|
		//|                 B2(FullWidth)                  |
		//|----------------------------------------------------|
		//

		varparams=Object.freeze({
			outerWidth:width,
			outerHeight:height,
			padding:padding,
			availableWidth:availableWidth,
			vBoxMaxWidth:availableWidth/2/verticalBoxes.length,
			hBoxMaxHeight:availableHeight/2
		});
		varchartArea=extend({
			maxPadding:extend({},padding),
			w:availableWidth,
			h:availableHeight,
			x:padding.left,
			y:padding.top
		},padding);

		setLayoutDims(verticalBoxes.concat(horizontalBoxes),params);

		//Firstfitverticalboxes
		fitBoxes(verticalBoxes,chartArea,params);

		//Thenfithorizontalboxes
		if(fitBoxes(horizontalBoxes,chartArea,params)){
			//iftheareachanged,re-fitverticalboxes
			fitBoxes(verticalBoxes,chartArea,params);
		}

		handleMaxPadding(chartArea);

		//Finallyplacetheboxestocorrectcoordinates
		placeBoxes(boxes.leftAndTop,chartArea,params);

		//Movetooppositesideofchart
		chartArea.x+=chartArea.w;
		chartArea.y+=chartArea.h;

		placeBoxes(boxes.rightAndBottom,chartArea,params);

		chart.chartArea={
			left:chartArea.left,
			top:chartArea.top,
			right:chartArea.left+chartArea.w,
			bottom:chartArea.top+chartArea.h
		};

		//FinallyupdateboxesinchartArea(radialscaleforexample)
		helpers$1.each(boxes.chartArea,function(layout){
			varbox=layout.box;
			extend(box,chart.chartArea);
			box.update(chartArea.w,chartArea.h);
		});
	}
};

/**
 *Platformfallbackimplementation(minimal).
 *@seehttps://github.com/chartjs/Chart.js/pull/4591#issuecomment-319575939
 */

varplatform_basic={
	acquireContext:function(item){
		if(item&&item.canvas){
			//Supportforanyobjectassociatedtoacanvas(includingacontext2d)
			item=item.canvas;
		}

		returnitem&&item.getContext('2d')||null;
	}
};

varplatform_dom="/*\n*DOMelementrenderingdetection\n*https://davidwalsh.name/detect-node-insertion\n*/\n@keyframeschartjs-render-animation{\n\tfrom{opacity:0.99;}\n\tto{opacity:1;}\n}\n\n.chartjs-render-monitor{\n\tanimation:chartjs-render-animation0.001s;\n}\n\n/*\n*DOMelementresizingdetection\n*https://github.com/marcj/css-element-queries\n*/\n.chartjs-size-monitor,\n.chartjs-size-monitor-expand,\n.chartjs-size-monitor-shrink{\n\tposition:absolute;\n\tdirection:ltr;\n\tleft:0;\n\ttop:0;\n\tright:0;\n\tbottom:0;\n\toverflow:hidden;\n\tpointer-events:none;\n\tvisibility:hidden;\n\tz-index:-1;\n}\n\n.chartjs-size-monitor-expand>div{\n\tposition:absolute;\n\twidth:1000000px;\n\theight:1000000px;\n\tleft:0;\n\ttop:0;\n}\n\n.chartjs-size-monitor-shrink>div{\n\tposition:absolute;\n\twidth:200%;\n\theight:200%;\n\tleft:0;\n\ttop:0;\n}\n";

varplatform_dom$1=/*#__PURE__*/Object.freeze({
__proto__:null,
'default':platform_dom
});

varstylesheet=getCjsExportFromNamespace(platform_dom$1);

varEXPANDO_KEY='$chartjs';
varCSS_PREFIX='chartjs-';
varCSS_SIZE_MONITOR=CSS_PREFIX+'size-monitor';
varCSS_RENDER_MONITOR=CSS_PREFIX+'render-monitor';
varCSS_RENDER_ANIMATION=CSS_PREFIX+'render-animation';
varANIMATION_START_EVENTS=['animationstart','webkitAnimationStart'];

/**
 *DOMeventtypes->Chart.jseventtypes.
 *Note:onlyeventswithdifferenttypesaremapped.
 *@seehttps://developer.mozilla.org/en-US/docs/Web/Events
 */
varEVENT_TYPES={
	touchstart:'mousedown',
	touchmove:'mousemove',
	touchend:'mouseup',
	pointerenter:'mouseenter',
	pointerdown:'mousedown',
	pointermove:'mousemove',
	pointerup:'mouseup',
	pointerleave:'mouseout',
	pointerout:'mouseout'
};

/**
 *The"used"sizeisthefinalvalueofadimensionpropertyafterallcalculationshave
 *beenperformed.Thismethodusesthecomputedstyleof`element`butreturnsundefined
 *ifthecomputedstyleisnotexpressedinpixels.Thatcanhappeninsomecaseswhere
 *`element`hasasizerelativetoitsparentandthislastoneisnotyetdisplayed,
 *forexamplebecauseof`display:none`onaparentnode.
 *@seehttps://developer.mozilla.org/en-US/docs/Web/CSS/used_value
 *@returns{number}Sizeinpixelsorundefinedifunknown.
 */
functionreadUsedSize(element,property){
	varvalue=helpers$1.getStyle(element,property);
	varmatches=value&&value.match(/^(\d+)(\.\d+)?px$/);
	returnmatches?Number(matches[1]):undefined;
}

/**
 *Initializesthecanvasstyleandrendersizewithoutmodifyingthecanvasdisplaysize,
 *sinceresponsivenessishandledbythecontroller.resize()method.Theconfigisused
 *todeterminetheaspectratiotoapplyincasenoexplicitheighthasbeenspecified.
 */
functioninitCanvas(canvas,config){
	varstyle=canvas.style;

	//NOTE(SB)canvas.getAttribute('width')!==canvas.width:inthefirstcaseit
	//returnsnullor''ifnoexplicitvaluehasbeensettothecanvasattribute.
	varrenderHeight=canvas.getAttribute('height');
	varrenderWidth=canvas.getAttribute('width');

	//Chart.jsmodifiessomecanvasvaluesthatwewanttorestoreondestroy
	canvas[EXPANDO_KEY]={
		initial:{
			height:renderHeight,
			width:renderWidth,
			style:{
				display:style.display,
				height:style.height,
				width:style.width
			}
		}
	};

	//Forcecanvastodisplayasblocktoavoidextraspacecausedbyinline
	//elements,whichwouldinterferewiththeresponsiveresizeprocess.
	//https://github.com/chartjs/Chart.js/issues/2538
	style.display=style.display||'block';

	if(renderWidth===null||renderWidth===''){
		vardisplayWidth=readUsedSize(canvas,'width');
		if(displayWidth!==undefined){
			canvas.width=displayWidth;
		}
	}

	if(renderHeight===null||renderHeight===''){
		if(canvas.style.height===''){
			//Ifnoexplicitrenderheightandstyleheight,let'sapplytheaspectratio,
			//whichonecanbespecifiedbytheuserbutalsobychartsasdefaultoption
			//(i.e.options.aspectRatio).Ifnotspecified,usecanvasaspectratioof2.
			canvas.height=canvas.width/(config.options.aspectRatio||2);
		}else{
			vardisplayHeight=readUsedSize(canvas,'height');
			if(displayWidth!==undefined){
				canvas.height=displayHeight;
			}
		}
	}

	returncanvas;
}

/**
 *DetectssupportforoptionsobjectargumentinaddEventListener.
 *https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener#Safely_detecting_option_support
 *@private
 */
varsupportsEventListenerOptions=(function(){
	varsupports=false;
	try{
		varoptions=Object.defineProperty({},'passive',{
			//eslint-disable-next-linegetter-return
			get:function(){
				supports=true;
			}
		});
		window.addEventListener('e',null,options);
	}catch(e){
		//continueregardlessoferror
	}
	returnsupports;
}());

//DefaultpassivetotrueasexpectedbyChromefor'touchstart'and'touchend'events.
//https://github.com/chartjs/Chart.js/issues/4287
vareventListenerOptions=supportsEventListenerOptions?{passive:true}:false;

functionaddListener(node,type,listener){
	node.addEventListener(type,listener,eventListenerOptions);
}

functionremoveListener(node,type,listener){
	node.removeEventListener(type,listener,eventListenerOptions);
}

functioncreateEvent(type,chart,x,y,nativeEvent){
	return{
		type:type,
		chart:chart,
		native:nativeEvent||null,
		x:x!==undefined?x:null,
		y:y!==undefined?y:null,
	};
}

functionfromNativeEvent(event,chart){
	vartype=EVENT_TYPES[event.type]||event.type;
	varpos=helpers$1.getRelativePosition(event,chart);
	returncreateEvent(type,chart,pos.x,pos.y,event);
}

functionthrottled(fn,thisArg){
	varticking=false;
	varargs=[];

	returnfunction(){
		args=Array.prototype.slice.call(arguments);
		thisArg=thisArg||this;

		if(!ticking){
			ticking=true;
			helpers$1.requestAnimFrame.call(window,function(){
				ticking=false;
				fn.apply(thisArg,args);
			});
		}
	};
}

functioncreateDiv(cls){
	varel=document.createElement('div');
	el.className=cls||'';
	returnel;
}

//Implementationbasedonhttps://github.com/marcj/css-element-queries
functioncreateResizer(handler){
	varmaxSize=1000000;

	//NOTE(SB)Don'tuseinnerHTMLbecauseitcouldbeconsideredunsafe.
	//https://github.com/chartjs/Chart.js/issues/5902
	varresizer=createDiv(CSS_SIZE_MONITOR);
	varexpand=createDiv(CSS_SIZE_MONITOR+'-expand');
	varshrink=createDiv(CSS_SIZE_MONITOR+'-shrink');

	expand.appendChild(createDiv());
	shrink.appendChild(createDiv());

	resizer.appendChild(expand);
	resizer.appendChild(shrink);
	resizer._reset=function(){
		expand.scrollLeft=maxSize;
		expand.scrollTop=maxSize;
		shrink.scrollLeft=maxSize;
		shrink.scrollTop=maxSize;
	};

	varonScroll=function(){
		resizer._reset();
		handler();
	};

	addListener(expand,'scroll',onScroll.bind(expand,'expand'));
	addListener(shrink,'scroll',onScroll.bind(shrink,'shrink'));

	returnresizer;
}

//https://davidwalsh.name/detect-node-insertion
functionwatchForRender(node,handler){
	varexpando=node[EXPANDO_KEY]||(node[EXPANDO_KEY]={});
	varproxy=expando.renderProxy=function(e){
		if(e.animationName===CSS_RENDER_ANIMATION){
			handler();
		}
	};

	helpers$1.each(ANIMATION_START_EVENTS,function(type){
		addListener(node,type,proxy);
	});

	//#4737:ChromemightskiptheCSSanimationwhentheCSS_RENDER_MONITORclass
	//isremovedthenaddedbackimmediately(sameanimationframe?).Accessingthe
	//`offsetParent`propertywillforceareflowandre-evaluatetheCSSanimation.
	//https://gist.github.com/paulirish/5d52fb081b3570c81e3a#box-metrics
	//https://github.com/chartjs/Chart.js/issues/4737
	expando.reflow=!!node.offsetParent;

	node.classList.add(CSS_RENDER_MONITOR);
}

functionunwatchForRender(node){
	varexpando=node[EXPANDO_KEY]||{};
	varproxy=expando.renderProxy;

	if(proxy){
		helpers$1.each(ANIMATION_START_EVENTS,function(type){
			removeListener(node,type,proxy);
		});

		deleteexpando.renderProxy;
	}

	node.classList.remove(CSS_RENDER_MONITOR);
}

functionaddResizeListener(node,listener,chart){
	varexpando=node[EXPANDO_KEY]||(node[EXPANDO_KEY]={});

	//Let'skeeptrackofthisaddedresizerandthusavoidDOMquerywhenremovingit.
	varresizer=expando.resizer=createResizer(throttled(function(){
		if(expando.resizer){
			varcontainer=chart.options.maintainAspectRatio&&node.parentNode;
			varw=container?container.clientWidth:0;
			listener(createEvent('resize',chart));
			if(container&&container.clientWidth<w&&chart.canvas){
				//Ifthecontainersizeshrankduringchartresize,let'sassume
				//scrollbarappeared.Soweresizeagainwiththescrollbarvisible-
				//effectivelymakingchartsmallerandthescrollbarhiddenagain.
				//Becauseweareinside`throttled`,andcurrently`ticking`,scroll
				//eventsareignoredduringthiswhole2resizeprocess.
				//Ifweassumedwrongandsomethingelsehappened,weareresizing
				//twiceinaframe(potentialperformanceissue)
				listener(createEvent('resize',chart));
			}
		}
	}));

	//Theresizerneedstobeattachedtothenodeparent,sowefirstneedtobe
	//surethat`node`isattachedtotheDOMbeforeinjectingtheresizerelement.
	watchForRender(node,function(){
		if(expando.resizer){
			varcontainer=node.parentNode;
			if(container&&container!==resizer.parentNode){
				container.insertBefore(resizer,container.firstChild);
			}

			//Thecontainersizemighthavechanged,let'sresettheresizerstate.
			resizer._reset();
		}
	});
}

functionremoveResizeListener(node){
	varexpando=node[EXPANDO_KEY]||{};
	varresizer=expando.resizer;

	deleteexpando.resizer;
	unwatchForRender(node);

	if(resizer&&resizer.parentNode){
		resizer.parentNode.removeChild(resizer);
	}
}

/**
 *InjectsCSSstylesinlineifthestylesarenotalreadypresent.
 *@param{HTMLDocument|ShadowRoot}rootNode-thenodetocontainthe<style>.
 *@param{string}css-theCSStobeinjected.
 */
functioninjectCSS(rootNode,css){
	//https://stackoverflow.com/q/3922139
	varexpando=rootNode[EXPANDO_KEY]||(rootNode[EXPANDO_KEY]={});
	if(!expando.containsStyles){
		expando.containsStyles=true;
		css='/*Chart.js*/\n'+css;
		varstyle=document.createElement('style');
		style.setAttribute('type','text/css');
		style.appendChild(document.createTextNode(css));
		rootNode.appendChild(style);
	}
}

varplatform_dom$2={
	/**
	*When`true`,preventstheautomaticinjectionofthestylesheetrequiredto
	*correctlydetectwhenthechartisaddedtotheDOMandthenresized.This
	*switchhasbeenaddedtoallowexternalstylesheet(`dist/Chart(.min)?.js`)
	*tobemanuallyimportedtomakethislibrarycompatiblewithanyCSP.
	*Seehttps://github.com/chartjs/Chart.js/issues/5208
	*/
	disableCSSInjection:false,

	/**
	*Thispropertyholdswhetherthisplatformisenabledforthecurrentenvironment.
	*Currentlyusedbyplatform.jstoselecttheproperimplementation.
	*@private
	*/
	_enabled:typeofwindow!=='undefined'&&typeofdocument!=='undefined',

	/**
	*Initializesresourcesthatdependonplatformoptions.
	*@param{HTMLCanvasElement}canvas-TheCanvaselement.
	*@private
	*/
	_ensureLoaded:function(canvas){
		if(!this.disableCSSInjection){
			//IfthecanvasisinashadowDOM,thenthestylesmustalsobeinserted
			//intothesameshadowDOM.
			//https://github.com/chartjs/Chart.js/issues/5763
			varroot=canvas.getRootNode?canvas.getRootNode():document;
			vartargetNode=root.host?root:document.head;
			injectCSS(targetNode,stylesheet);
		}
	},

	acquireContext:function(item,config){
		if(typeofitem==='string'){
			item=document.getElementById(item);
		}elseif(item.length){
			//Supportforarraybasedqueries(suchasjQuery)
			item=item[0];
		}

		if(item&&item.canvas){
			//Supportforanyobjectassociatedtoacanvas(includingacontext2d)
			item=item.canvas;
		}

		//Topreventcanvasfingerprinting,someadd-onsundefinethegetContext
		//method,forexample:https://github.com/kkapsner/CanvasBlocker
		//https://github.com/chartjs/Chart.js/issues/2807
		varcontext=item&&item.getContext&&item.getContext('2d');

		//`instanceofHTMLCanvasElement/CanvasRenderingContext2D`failswhentheitemis
		//insideaniframeorwhenrunninginaprotectedenvironment.Wecouldguessthe
		//typesfromtheirtoString()valuebutlet'skeepthingsflexibleandassumeit's
		//asufficientconditioniftheitemhasacontext2Dwhichhasitemas`canvas`.
		//https://github.com/chartjs/Chart.js/issues/3887
		//https://github.com/chartjs/Chart.js/issues/4102
		//https://github.com/chartjs/Chart.js/issues/4152
		if(context&&context.canvas===item){
			//Loadplatformresourcesonfirstchartcreation,tomakeitpossibleto
			//importthelibrarybeforesettingplatformoptions.
			this._ensureLoaded(item);
			initCanvas(item,config);
			returncontext;
		}

		returnnull;
	},

	releaseContext:function(context){
		varcanvas=context.canvas;
		if(!canvas[EXPANDO_KEY]){
			return;
		}

		varinitial=canvas[EXPANDO_KEY].initial;
		['height','width'].forEach(function(prop){
			varvalue=initial[prop];
			if(helpers$1.isNullOrUndef(value)){
				canvas.removeAttribute(prop);
			}else{
				canvas.setAttribute(prop,value);
			}
		});

		helpers$1.each(initial.style||{},function(value,key){
			canvas.style[key]=value;
		});

		//Thecanvasrendersizemighthavebeenchanged(andthusthestatestackdiscarded),
		//wecan'tusesave()andrestore()torestoretheinitialstate.Somakesurethatat
		//leastthecanvascontextisresettothedefaultstatebysettingthecanvaswidth.
		//https://www.w3.org/TR/2011/WD-html5-20110525/the-canvas-element.html
		//eslint-disable-next-lineno-self-assign
		canvas.width=canvas.width;

		deletecanvas[EXPANDO_KEY];
	},

	addEventListener:function(chart,type,listener){
		varcanvas=chart.canvas;
		if(type==='resize'){
			//Note:theresizeeventisnotsupportedonallbrowsers.
			addResizeListener(canvas,listener,chart);
			return;
		}

		varexpando=listener[EXPANDO_KEY]||(listener[EXPANDO_KEY]={});
		varproxies=expando.proxies||(expando.proxies={});
		varproxy=proxies[chart.id+'_'+type]=function(event){
			listener(fromNativeEvent(event,chart));
		};

		addListener(canvas,type,proxy);
	},

	removeEventListener:function(chart,type,listener){
		varcanvas=chart.canvas;
		if(type==='resize'){
			//Note:theresizeeventisnotsupportedonallbrowsers.
			removeResizeListener(canvas);
			return;
		}

		varexpando=listener[EXPANDO_KEY]||{};
		varproxies=expando.proxies||{};
		varproxy=proxies[chart.id+'_'+type];
		if(!proxy){
			return;
		}

		removeListener(canvas,type,proxy);
	}
};

//DEPRECATIONS

/**
 *Providedforbackwardcompatibility,useEventTarget.addEventListenerinstead.
 *EventTarget.addEventListenercompatibility:Chrome,Opera7,Safari,FF1.5+,IE9+
 *@seehttps://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener
 *@functionChart.helpers.addEvent
 *@deprecatedsinceversion2.7.0
 *@todoremoveatversion3
 *@private
 */
helpers$1.addEvent=addListener;

/**
 *Providedforbackwardcompatibility,useEventTarget.removeEventListenerinstead.
 *EventTarget.removeEventListenercompatibility:Chrome,Opera7,Safari,FF1.5+,IE9+
 *@seehttps://developer.mozilla.org/en-US/docs/Web/API/EventTarget/removeEventListener
 *@functionChart.helpers.removeEvent
 *@deprecatedsinceversion2.7.0
 *@todoremoveatversion3
 *@private
 */
helpers$1.removeEvent=removeListener;

//@TODOMakepossibletoselectanotherplatformatbuildtime.
varimplementation=platform_dom$2._enabled?platform_dom$2:platform_basic;

/**
 *@namespaceChart.platform
 *@seehttps://chartjs.gitbooks.io/proposals/content/Platform.html
 *@since2.4.0
 */
varplatform=helpers$1.extend({
	/**
	*@since2.7.0
	*/
	initialize:function(){},

	/**
	*Calledatchartconstructiontime,returnsacontext2dinstanceimplementing
	*the[W3CCanvas2DContextAPIstandard]{@linkhttps://www.w3.org/TR/2dcontext/}.
	*@param{*}item-Thenativeitemfromwhichtoacquirecontext(platformspecific)
	*@param{object}options-Thechartoptions
	*@returns{CanvasRenderingContext2D}context2dinstance
	*/
	acquireContext:function(){},

	/**
	*Calledatchartdestructiontime,releasesanyresourcesassociatedtothecontext
	*previouslyreturnedbytheacquireContext()method.
	*@param{CanvasRenderingContext2D}context-Thecontext2dinstance
	*@returns{boolean}trueifthemethodsucceeded,elsefalse
	*/
	releaseContext:function(){},

	/**
	*Registersthespecifiedlisteneronthegivenchart.
	*@param{Chart}chart-Chartfromwhichtolistenforevent
	*@param{string}type-The({@linkIEvent})typetolistenfor
	*@param{function}listener-Receivesanotification(anobjectthatimplements
	*the{@linkIEvent}interface)whenaneventofthespecifiedtypeoccurs.
	*/
	addEventListener:function(){},

	/**
	*RemovesthespecifiedlistenerpreviouslyregisteredwithaddEventListener.
	*@param{Chart}chart-Chartfromwhichtoremovethelistener
	*@param{string}type-The({@linkIEvent})typetoremove
	*@param{function}listener-Thelistenerfunctiontoremovefromtheeventtarget.
	*/
	removeEventListener:function(){}

},implementation);

core_defaults._set('global',{
	plugins:{}
});

/**
 *Thepluginservicesingleton
 *@namespaceChart.plugins
 *@since2.1.0
 */
varcore_plugins={
	/**
	*Globallyregisteredplugins.
	*@private
	*/
	_plugins:[],

	/**
	*Thisidentifierisusedtoinvalidatethedescriptorscacheattachedtoeachchart
	*whenaglobalpluginisregisteredorunregistered.Inthiscase,thecacheIDis
	*incrementedanddescriptorsareregeneratedduringfollowingAPIcalls.
	*@private
	*/
	_cacheId:0,

	/**
	*Registersthegivenplugin(s)ifnotalreadyregistered.
	*@param{IPlugin[]|IPlugin}pluginsplugininstance(s).
	*/
	register:function(plugins){
		varp=this._plugins;
		([]).concat(plugins).forEach(function(plugin){
			if(p.indexOf(plugin)===-1){
				p.push(plugin);
			}
		});

		this._cacheId++;
	},

	/**
	*Unregistersthegivenplugin(s)onlyifregistered.
	*@param{IPlugin[]|IPlugin}pluginsplugininstance(s).
	*/
	unregister:function(plugins){
		varp=this._plugins;
		([]).concat(plugins).forEach(function(plugin){
			varidx=p.indexOf(plugin);
			if(idx!==-1){
				p.splice(idx,1);
			}
		});

		this._cacheId++;
	},

	/**
	*Removeallregisteredplugins.
	*@since2.1.5
	*/
	clear:function(){
		this._plugins=[];
		this._cacheId++;
	},

	/**
	*Returnsthenumberofregisteredplugins?
	*@returns{number}
	*@since2.1.5
	*/
	count:function(){
		returnthis._plugins.length;
	},

	/**
	*Returnsallregisteredplugininstances.
	*@returns{IPlugin[]}arrayofpluginobjects.
	*@since2.1.5
	*/
	getAll:function(){
		returnthis._plugins;
	},

	/**
	*Callsenabledpluginsfor`chart`onthespecifiedhookandwiththegivenargs.
	*Thismethodimmediatelyreturnsassoonasapluginexplicitlyreturnsfalse.The
	*returnedvaluecanbeused,forinstance,tointerruptthecurrentaction.
	*@param{Chart}chart-Thechartinstanceforwhichpluginsshouldbecalled.
	*@param{string}hook-Thenameofthepluginmethodtocall(e.g.'beforeUpdate').
	*@param{Array}[args]-Extraargumentstoapplytothehookcall.
	*@returns{boolean}falseifanyofthepluginsreturnfalse,elsereturnstrue.
	*/
	notify:function(chart,hook,args){
		vardescriptors=this.descriptors(chart);
		varilen=descriptors.length;
		vari,descriptor,plugin,params,method;

		for(i=0;i<ilen;++i){
			descriptor=descriptors[i];
			plugin=descriptor.plugin;
			method=plugin[hook];
			if(typeofmethod==='function'){
				params=[chart].concat(args||[]);
				params.push(descriptor.options);
				if(method.apply(plugin,params)===false){
					returnfalse;
				}
			}
		}

		returntrue;
	},

	/**
	*Returnsdescriptorsofenabledpluginsforthegivenchart.
	*@returns{object[]}[{plugin,options}]
	*@private
	*/
	descriptors:function(chart){
		varcache=chart.$plugins||(chart.$plugins={});
		if(cache.id===this._cacheId){
			returncache.descriptors;
		}

		varplugins=[];
		vardescriptors=[];
		varconfig=(chart&&chart.config)||{};
		varoptions=(config.options&&config.options.plugins)||{};

		this._plugins.concat(config.plugins||[]).forEach(function(plugin){
			varidx=plugins.indexOf(plugin);
			if(idx!==-1){
				return;
			}

			varid=plugin.id;
			varopts=options[id];
			if(opts===false){
				return;
			}

			if(opts===true){
				opts=helpers$1.clone(core_defaults.global.plugins[id]);
			}

			plugins.push(plugin);
			descriptors.push({
				plugin:plugin,
				options:opts||{}
			});
		});

		cache.descriptors=descriptors;
		cache.id=this._cacheId;
		returndescriptors;
	},

	/**
	*Invalidatescacheforthegivenchart:descriptorsholdareferenceonpluginoption,
	*butinsomecases,thisreferencecanbechangedbytheuserwhenupdatingoptions.
	*https://github.com/chartjs/Chart.js/issues/5111#issuecomment-355934167
	*@private
	*/
	_invalidate:function(chart){
		deletechart.$plugins;
	}
};

varcore_scaleService={
	//Scaleregistrationobject.Extensionscanregisternewscaletypes(suchaslogorDBscales)andthen
	//usethenewchartoptionstograbthecorrectscale
	constructors:{},
	//UsearegistrationfunctionsothatwecanmovetoanES6mapwhenwenolongerneedtosupport
	//oldbrowsers

	//Scaleconfigdefaults
	defaults:{},
	registerScaleType:function(type,scaleConstructor,scaleDefaults){
		this.constructors[type]=scaleConstructor;
		this.defaults[type]=helpers$1.clone(scaleDefaults);
	},
	getScaleConstructor:function(type){
		returnthis.constructors.hasOwnProperty(type)?this.constructors[type]:undefined;
	},
	getScaleDefaults:function(type){
		//Returnthescaledefaultsmergedwiththeglobalsettingssothatwealwaysusethelatestones
		returnthis.defaults.hasOwnProperty(type)?helpers$1.merge(Object.create(null),[core_defaults.scale,this.defaults[type]]):{};
	},
	updateScaleDefaults:function(type,additions){
		varme=this;
		if(me.defaults.hasOwnProperty(type)){
			me.defaults[type]=helpers$1.extend(me.defaults[type],additions);
		}
	},
	addScalesToLayout:function(chart){
		//Addseachscaletothechart.boxesarraytobesizedaccordingly
		helpers$1.each(chart.scales,function(scale){
			//SetILayoutItemparametersforbackwardscompatibility
			scale.fullWidth=scale.options.fullWidth;
			scale.position=scale.options.position;
			scale.weight=scale.options.weight;
			core_layouts.addBox(chart,scale);
		});
	}
};

varvalueOrDefault$8=helpers$1.valueOrDefault;
vargetRtlHelper=helpers$1.rtl.getRtlAdapter;

core_defaults._set('global',{
	tooltips:{
		enabled:true,
		custom:null,
		mode:'nearest',
		position:'average',
		intersect:true,
		backgroundColor:'rgba(0,0,0,0.8)',
		titleFontStyle:'bold',
		titleSpacing:2,
		titleMarginBottom:6,
		titleFontColor:'#fff',
		titleAlign:'left',
		bodySpacing:2,
		bodyFontColor:'#fff',
		bodyAlign:'left',
		footerFontStyle:'bold',
		footerSpacing:2,
		footerMarginTop:6,
		footerFontColor:'#fff',
		footerAlign:'left',
		yPadding:6,
		xPadding:6,
		caretPadding:2,
		caretSize:5,
		cornerRadius:6,
		multiKeyBackground:'#fff',
		displayColors:true,
		borderColor:'rgba(0,0,0,0)',
		borderWidth:0,
		callbacks:{
			//Argsare:(tooltipItems,data)
			beforeTitle:helpers$1.noop,
			title:function(tooltipItems,data){
				vartitle='';
				varlabels=data.labels;
				varlabelCount=labels?labels.length:0;

				if(tooltipItems.length>0){
					varitem=tooltipItems[0];
					if(item.label){
						title=item.label;
					}elseif(item.xLabel){
						title=item.xLabel;
					}elseif(labelCount>0&&item.index<labelCount){
						title=labels[item.index];
					}
				}

				returntitle;
			},
			afterTitle:helpers$1.noop,

			//Argsare:(tooltipItems,data)
			beforeBody:helpers$1.noop,

			//Argsare:(tooltipItem,data)
			beforeLabel:helpers$1.noop,
			label:function(tooltipItem,data){
				varlabel=data.datasets[tooltipItem.datasetIndex].label||'';

				if(label){
					label+=':';
				}
				if(!helpers$1.isNullOrUndef(tooltipItem.value)){
					label+=tooltipItem.value;
				}else{
					label+=tooltipItem.yLabel;
				}
				returnlabel;
			},
			labelColor:function(tooltipItem,chart){
				varmeta=chart.getDatasetMeta(tooltipItem.datasetIndex);
				varactiveElement=meta.data[tooltipItem.index];
				varview=activeElement._view;
				return{
					borderColor:view.borderColor,
					backgroundColor:view.backgroundColor
				};
			},
			labelTextColor:function(){
				returnthis._options.bodyFontColor;
			},
			afterLabel:helpers$1.noop,

			//Argsare:(tooltipItems,data)
			afterBody:helpers$1.noop,

			//Argsare:(tooltipItems,data)
			beforeFooter:helpers$1.noop,
			footer:helpers$1.noop,
			afterFooter:helpers$1.noop
		}
	}
});

varpositioners={
	/**
	*Averagemodeplacesthetooltipattheaveragepositionoftheelementsshown
	*@functionChart.Tooltip.positioners.average
	*@paramelements{ChartElement[]}theelementsbeingdisplayedinthetooltip
	*@returns{object}tooltipposition
	*/
	average:function(elements){
		if(!elements.length){
			returnfalse;
		}

		vari,len;
		varx=0;
		vary=0;
		varcount=0;

		for(i=0,len=elements.length;i<len;++i){
			varel=elements[i];
			if(el&&el.hasValue()){
				varpos=el.tooltipPosition();
				x+=pos.x;
				y+=pos.y;
				++count;
			}
		}

		return{
			x:x/count,
			y:y/count
		};
	},

	/**
	*Getsthetooltippositionnearestoftheitemnearesttotheeventposition
	*@functionChart.Tooltip.positioners.nearest
	*@paramelements{Chart.Element[]}thetooltipelements
	*@parameventPosition{object}thepositionoftheeventincanvascoordinates
	*@returns{object}thetooltipposition
	*/
	nearest:function(elements,eventPosition){
		varx=eventPosition.x;
		vary=eventPosition.y;
		varminDistance=Number.POSITIVE_INFINITY;
		vari,len,nearestElement;

		for(i=0,len=elements.length;i<len;++i){
			varel=elements[i];
			if(el&&el.hasValue()){
				varcenter=el.getCenterPoint();
				vard=helpers$1.distanceBetweenPoints(eventPosition,center);

				if(d<minDistance){
					minDistance=d;
					nearestElement=el;
				}
			}
		}

		if(nearestElement){
			vartp=nearestElement.tooltipPosition();
			x=tp.x;
			y=tp.y;
		}

		return{
			x:x,
			y:y
		};
	}
};

//Helpertopushorconcatbasedonifthe2ndparameterisanarrayornot
functionpushOrConcat(base,toPush){
	if(toPush){
		if(helpers$1.isArray(toPush)){
			//base=base.concat(toPush);
			Array.prototype.push.apply(base,toPush);
		}else{
			base.push(toPush);
		}
	}

	returnbase;
}

/**
 *Returnsarrayofstringssplitbynewline
 *@param{string}value-Thevaluetosplitbynewline.
 *@returns{string[]}valueifnewlinepresent-ReturnedfromStringsplit()method
 *@function
 */
functionsplitNewlines(str){
	if((typeofstr==='string'||strinstanceofString)&&str.indexOf('\n')>-1){
		returnstr.split('\n');
	}
	returnstr;
}


/**
 *Privatehelpertocreateatooltipitemmodel
 *@paramelement-thechartelement(point,arc,bar)tocreatethetooltipitemfor
 *@returnnewtooltipitem
 */
functioncreateTooltipItem(element){
	varxScale=element._xScale;
	varyScale=element._yScale||element._scale;//handleradar||polarAreacharts
	varindex=element._index;
	vardatasetIndex=element._datasetIndex;
	varcontroller=element._chart.getDatasetMeta(datasetIndex).controller;
	varindexScale=controller._getIndexScale();
	varvalueScale=controller._getValueScale();

	return{
		xLabel:xScale?xScale.getLabelForIndex(index,datasetIndex):'',
		yLabel:yScale?yScale.getLabelForIndex(index,datasetIndex):'',
		label:indexScale?''+indexScale.getLabelForIndex(index,datasetIndex):'',
		value:valueScale?''+valueScale.getLabelForIndex(index,datasetIndex):'',
		index:index,
		datasetIndex:datasetIndex,
		x:element._model.x,
		y:element._model.y
	};
}

/**
 *Helpertogettheresetmodelforthetooltip
 *@paramtooltipOpts{object}thetooltipoptions
 */
functiongetBaseModel(tooltipOpts){
	varglobalDefaults=core_defaults.global;

	return{
		//Positioning
		xPadding:tooltipOpts.xPadding,
		yPadding:tooltipOpts.yPadding,
		xAlign:tooltipOpts.xAlign,
		yAlign:tooltipOpts.yAlign,

		//Drawingdirectionandtextdirection
		rtl:tooltipOpts.rtl,
		textDirection:tooltipOpts.textDirection,

		//Body
		bodyFontColor:tooltipOpts.bodyFontColor,
		_bodyFontFamily:valueOrDefault$8(tooltipOpts.bodyFontFamily,globalDefaults.defaultFontFamily),
		_bodyFontStyle:valueOrDefault$8(tooltipOpts.bodyFontStyle,globalDefaults.defaultFontStyle),
		_bodyAlign:tooltipOpts.bodyAlign,
		bodyFontSize:valueOrDefault$8(tooltipOpts.bodyFontSize,globalDefaults.defaultFontSize),
		bodySpacing:tooltipOpts.bodySpacing,

		//Title
		titleFontColor:tooltipOpts.titleFontColor,
		_titleFontFamily:valueOrDefault$8(tooltipOpts.titleFontFamily,globalDefaults.defaultFontFamily),
		_titleFontStyle:valueOrDefault$8(tooltipOpts.titleFontStyle,globalDefaults.defaultFontStyle),
		titleFontSize:valueOrDefault$8(tooltipOpts.titleFontSize,globalDefaults.defaultFontSize),
		_titleAlign:tooltipOpts.titleAlign,
		titleSpacing:tooltipOpts.titleSpacing,
		titleMarginBottom:tooltipOpts.titleMarginBottom,

		//Footer
		footerFontColor:tooltipOpts.footerFontColor,
		_footerFontFamily:valueOrDefault$8(tooltipOpts.footerFontFamily,globalDefaults.defaultFontFamily),
		_footerFontStyle:valueOrDefault$8(tooltipOpts.footerFontStyle,globalDefaults.defaultFontStyle),
		footerFontSize:valueOrDefault$8(tooltipOpts.footerFontSize,globalDefaults.defaultFontSize),
		_footerAlign:tooltipOpts.footerAlign,
		footerSpacing:tooltipOpts.footerSpacing,
		footerMarginTop:tooltipOpts.footerMarginTop,

		//Appearance
		caretSize:tooltipOpts.caretSize,
		cornerRadius:tooltipOpts.cornerRadius,
		backgroundColor:tooltipOpts.backgroundColor,
		opacity:0,
		legendColorBackground:tooltipOpts.multiKeyBackground,
		displayColors:tooltipOpts.displayColors,
		borderColor:tooltipOpts.borderColor,
		borderWidth:tooltipOpts.borderWidth
	};
}

/**
 *Getthesizeofthetooltip
 */
functiongetTooltipSize(tooltip,model){
	varctx=tooltip._chart.ctx;

	varheight=model.yPadding*2;//TooltipPadding
	varwidth=0;

	//Countofalllinesinthebody
	varbody=model.body;
	varcombinedBodyLength=body.reduce(function(count,bodyItem){
		returncount+bodyItem.before.length+bodyItem.lines.length+bodyItem.after.length;
	},0);
	combinedBodyLength+=model.beforeBody.length+model.afterBody.length;

	vartitleLineCount=model.title.length;
	varfooterLineCount=model.footer.length;
	vartitleFontSize=model.titleFontSize;
	varbodyFontSize=model.bodyFontSize;
	varfooterFontSize=model.footerFontSize;

	height+=titleLineCount*titleFontSize;//TitleLines
	height+=titleLineCount?(titleLineCount-1)*model.titleSpacing:0;//TitleLineSpacing
	height+=titleLineCount?model.titleMarginBottom:0;//Title'sbottomMargin
	height+=combinedBodyLength*bodyFontSize;//BodyLines
	height+=combinedBodyLength?(combinedBodyLength-1)*model.bodySpacing:0;//BodyLineSpacing
	height+=footerLineCount?model.footerMarginTop:0;//FooterMargin
	height+=footerLineCount*(footerFontSize);//FooterLines
	height+=footerLineCount?(footerLineCount-1)*model.footerSpacing:0;//FooterLineSpacing

	//Titlewidth
	varwidthPadding=0;
	varmaxLineWidth=function(line){
		width=Math.max(width,ctx.measureText(line).width+widthPadding);
	};

	ctx.font=helpers$1.fontString(titleFontSize,model._titleFontStyle,model._titleFontFamily);
	helpers$1.each(model.title,maxLineWidth);

	//Bodywidth
	ctx.font=helpers$1.fontString(bodyFontSize,model._bodyFontStyle,model._bodyFontFamily);
	helpers$1.each(model.beforeBody.concat(model.afterBody),maxLineWidth);

	//Bodylinesmayincludesomeextrawidthduetothecolorbox
	widthPadding=model.displayColors?(bodyFontSize+2):0;
	helpers$1.each(body,function(bodyItem){
		helpers$1.each(bodyItem.before,maxLineWidth);
		helpers$1.each(bodyItem.lines,maxLineWidth);
		helpers$1.each(bodyItem.after,maxLineWidth);
	});

	//Resetbackto0
	widthPadding=0;

	//Footerwidth
	ctx.font=helpers$1.fontString(footerFontSize,model._footerFontStyle,model._footerFontFamily);
	helpers$1.each(model.footer,maxLineWidth);

	//Addpadding
	width+=2*model.xPadding;

	return{
		width:width,
		height:height
	};
}

/**
 *Helpertogetthealignmentofatooltipgiventhesize
 */
functiondetermineAlignment(tooltip,size){
	varmodel=tooltip._model;
	varchart=tooltip._chart;
	varchartArea=tooltip._chart.chartArea;
	varxAlign='center';
	varyAlign='center';

	if(model.y<size.height){
		yAlign='top';
	}elseif(model.y>(chart.height-size.height)){
		yAlign='bottom';
	}

	varlf,rf;//functionstodetermineleft,rightalignment
	varolf,orf;//functionstodetermineifleft/rightalignmentcausestooltiptogooutsidechart
	varyf;//functiontogettheyalignmentifthetooltipgoesoutsideoftheleftorrightedges
	varmidX=(chartArea.left+chartArea.right)/2;
	varmidY=(chartArea.top+chartArea.bottom)/2;

	if(yAlign==='center'){
		lf=function(x){
			returnx<=midX;
		};
		rf=function(x){
			returnx>midX;
		};
	}else{
		lf=function(x){
			returnx<=(size.width/2);
		};
		rf=function(x){
			returnx>=(chart.width-(size.width/2));
		};
	}

	olf=function(x){
		returnx+size.width+model.caretSize+model.caretPadding>chart.width;
	};
	orf=function(x){
		returnx-size.width-model.caretSize-model.caretPadding<0;
	};
	yf=function(y){
		returny<=midY?'top':'bottom';
	};

	if(lf(model.x)){
		xAlign='left';

		//Istooltiptoowideandgoesovertherightsideofthechart.?
		if(olf(model.x)){
			xAlign='center';
			yAlign=yf(model.y);
		}
	}elseif(rf(model.x)){
		xAlign='right';

		//Istooltiptoowideandgoesoutsideleftedgeofcanvas?
		if(orf(model.x)){
			xAlign='center';
			yAlign=yf(model.y);
		}
	}

	varopts=tooltip._options;
	return{
		xAlign:opts.xAlign?opts.xAlign:xAlign,
		yAlign:opts.yAlign?opts.yAlign:yAlign
	};
}

/**
 *Helpertogetthelocationatooltipneedstobeplacedatgiventheinitialposition(viathevm)andthesizeandalignment
 */
functiongetBackgroundPoint(vm,size,alignment,chart){
	//BackgroundPosition
	varx=vm.x;
	vary=vm.y;

	varcaretSize=vm.caretSize;
	varcaretPadding=vm.caretPadding;
	varcornerRadius=vm.cornerRadius;
	varxAlign=alignment.xAlign;
	varyAlign=alignment.yAlign;
	varpaddingAndSize=caretSize+caretPadding;
	varradiusAndPadding=cornerRadius+caretPadding;

	if(xAlign==='right'){
		x-=size.width;
	}elseif(xAlign==='center'){
		x-=(size.width/2);
		if(x+size.width>chart.width){
			x=chart.width-size.width;
		}
		if(x<0){
			x=0;
		}
	}

	if(yAlign==='top'){
		y+=paddingAndSize;
	}elseif(yAlign==='bottom'){
		y-=size.height+paddingAndSize;
	}else{
		y-=(size.height/2);
	}

	if(yAlign==='center'){
		if(xAlign==='left'){
			x+=paddingAndSize;
		}elseif(xAlign==='right'){
			x-=paddingAndSize;
		}
	}elseif(xAlign==='left'){
		x-=radiusAndPadding;
	}elseif(xAlign==='right'){
		x+=radiusAndPadding;
	}

	return{
		x:x,
		y:y
	};
}

functiongetAlignedX(vm,align){
	returnalign==='center'
		?vm.x+vm.width/2
		:align==='right'
			?vm.x+vm.width-vm.xPadding
			:vm.x+vm.xPadding;
}

/**
 *Helpertobuildbeforeandafterbodylines
 */
functiongetBeforeAfterBodyLines(callback){
	returnpushOrConcat([],splitNewlines(callback));
}

varexports$4=core_element.extend({
	initialize:function(){
		this._model=getBaseModel(this._options);
		this._lastActive=[];
	},

	//Getthetitle
	//Argsare:(tooltipItem,data)
	getTitle:function(){
		varme=this;
		varopts=me._options;
		varcallbacks=opts.callbacks;

		varbeforeTitle=callbacks.beforeTitle.apply(me,arguments);
		vartitle=callbacks.title.apply(me,arguments);
		varafterTitle=callbacks.afterTitle.apply(me,arguments);

		varlines=[];
		lines=pushOrConcat(lines,splitNewlines(beforeTitle));
		lines=pushOrConcat(lines,splitNewlines(title));
		lines=pushOrConcat(lines,splitNewlines(afterTitle));

		returnlines;
	},

	//Argsare:(tooltipItem,data)
	getBeforeBody:function(){
		returngetBeforeAfterBodyLines(this._options.callbacks.beforeBody.apply(this,arguments));
	},

	//Argsare:(tooltipItem,data)
	getBody:function(tooltipItems,data){
		varme=this;
		varcallbacks=me._options.callbacks;
		varbodyItems=[];

		helpers$1.each(tooltipItems,function(tooltipItem){
			varbodyItem={
				before:[],
				lines:[],
				after:[]
			};
			pushOrConcat(bodyItem.before,splitNewlines(callbacks.beforeLabel.call(me,tooltipItem,data)));
			pushOrConcat(bodyItem.lines,callbacks.label.call(me,tooltipItem,data));
			pushOrConcat(bodyItem.after,splitNewlines(callbacks.afterLabel.call(me,tooltipItem,data)));

			bodyItems.push(bodyItem);
		});

		returnbodyItems;
	},

	//Argsare:(tooltipItem,data)
	getAfterBody:function(){
		returngetBeforeAfterBodyLines(this._options.callbacks.afterBody.apply(this,arguments));
	},

	//GetthefooterandbeforeFooterandafterFooterlines
	//Argsare:(tooltipItem,data)
	getFooter:function(){
		varme=this;
		varcallbacks=me._options.callbacks;

		varbeforeFooter=callbacks.beforeFooter.apply(me,arguments);
		varfooter=callbacks.footer.apply(me,arguments);
		varafterFooter=callbacks.afterFooter.apply(me,arguments);

		varlines=[];
		lines=pushOrConcat(lines,splitNewlines(beforeFooter));
		lines=pushOrConcat(lines,splitNewlines(footer));
		lines=pushOrConcat(lines,splitNewlines(afterFooter));

		returnlines;
	},

	update:function(changed){
		varme=this;
		varopts=me._options;

		//NeedtoregeneratethemodelbecauseitsfasterthanusingextendanditisnecessaryduetotheoptimizationinChart.Element.transition
		//thatdoes_view=_modelifease===1.Thiscausesthe2ndtooltipupdatetosetpropertiesinboththeviewandmodelatthesametime
		//whichbreaksanyanimations.
		varexistingModel=me._model;
		varmodel=me._model=getBaseModel(opts);
		varactive=me._active;

		vardata=me._data;

		//Inthecasewhereactive.length===0weneedtokeeptheseatexistingvaluesforgoodanimations
		varalignment={
			xAlign:existingModel.xAlign,
			yAlign:existingModel.yAlign
		};
		varbackgroundPoint={
			x:existingModel.x,
			y:existingModel.y
		};
		vartooltipSize={
			width:existingModel.width,
			height:existingModel.height
		};
		vartooltipPosition={
			x:existingModel.caretX,
			y:existingModel.caretY
		};

		vari,len;

		if(active.length){
			model.opacity=1;

			varlabelColors=[];
			varlabelTextColors=[];
			tooltipPosition=positioners[opts.position].call(me,active,me._eventPosition);

			vartooltipItems=[];
			for(i=0,len=active.length;i<len;++i){
				tooltipItems.push(createTooltipItem(active[i]));
			}

			//Iftheuserprovidedafilterfunction,useittomodifythetooltipitems
			if(opts.filter){
				tooltipItems=tooltipItems.filter(function(a){
					returnopts.filter(a,data);
				});
			}

			//Iftheuserprovidedasortingfunction,useittomodifythetooltipitems
			if(opts.itemSort){
				tooltipItems=tooltipItems.sort(function(a,b){
					returnopts.itemSort(a,b,data);
				});
			}

			//Determinecolorsforboxes
			helpers$1.each(tooltipItems,function(tooltipItem){
				labelColors.push(opts.callbacks.labelColor.call(me,tooltipItem,me._chart));
				labelTextColors.push(opts.callbacks.labelTextColor.call(me,tooltipItem,me._chart));
			});


			//BuildtheTextLines
			model.title=me.getTitle(tooltipItems,data);
			model.beforeBody=me.getBeforeBody(tooltipItems,data);
			model.body=me.getBody(tooltipItems,data);
			model.afterBody=me.getAfterBody(tooltipItems,data);
			model.footer=me.getFooter(tooltipItems,data);

			//Initialpositioningandcolors
			model.x=tooltipPosition.x;
			model.y=tooltipPosition.y;
			model.caretPadding=opts.caretPadding;
			model.labelColors=labelColors;
			model.labelTextColors=labelTextColors;

			//datapoints
			model.dataPoints=tooltipItems;

			//Weneedtodeterminealignmentofthetooltip
			tooltipSize=getTooltipSize(this,model);
			alignment=determineAlignment(this,tooltipSize);
			//FinalSizeandPosition
			backgroundPoint=getBackgroundPoint(model,tooltipSize,alignment,me._chart);
		}else{
			model.opacity=0;
		}

		model.xAlign=alignment.xAlign;
		model.yAlign=alignment.yAlign;
		model.x=backgroundPoint.x;
		model.y=backgroundPoint.y;
		model.width=tooltipSize.width;
		model.height=tooltipSize.height;

		//Pointwherethecaretonthetooltippointsto
		model.caretX=tooltipPosition.x;
		model.caretY=tooltipPosition.y;

		me._model=model;

		if(changed&&opts.custom){
			opts.custom.call(me,model);
		}

		returnme;
	},

	drawCaret:function(tooltipPoint,size){
		varctx=this._chart.ctx;
		varvm=this._view;
		varcaretPosition=this.getCaretPosition(tooltipPoint,size,vm);

		ctx.lineTo(caretPosition.x1,caretPosition.y1);
		ctx.lineTo(caretPosition.x2,caretPosition.y2);
		ctx.lineTo(caretPosition.x3,caretPosition.y3);
	},
	getCaretPosition:function(tooltipPoint,size,vm){
		varx1,x2,x3,y1,y2,y3;
		varcaretSize=vm.caretSize;
		varcornerRadius=vm.cornerRadius;
		varxAlign=vm.xAlign;
		varyAlign=vm.yAlign;
		varptX=tooltipPoint.x;
		varptY=tooltipPoint.y;
		varwidth=size.width;
		varheight=size.height;

		if(yAlign==='center'){
			y2=ptY+(height/2);

			if(xAlign==='left'){
				x1=ptX;
				x2=x1-caretSize;
				x3=x1;

				y1=y2+caretSize;
				y3=y2-caretSize;
			}else{
				x1=ptX+width;
				x2=x1+caretSize;
				x3=x1;

				y1=y2-caretSize;
				y3=y2+caretSize;
			}
		}else{
			if(xAlign==='left'){
				x2=ptX+cornerRadius+(caretSize);
				x1=x2-caretSize;
				x3=x2+caretSize;
			}elseif(xAlign==='right'){
				x2=ptX+width-cornerRadius-caretSize;
				x1=x2-caretSize;
				x3=x2+caretSize;
			}else{
				x2=vm.caretX;
				x1=x2-caretSize;
				x3=x2+caretSize;
			}
			if(yAlign==='top'){
				y1=ptY;
				y2=y1-caretSize;
				y3=y1;
			}else{
				y1=ptY+height;
				y2=y1+caretSize;
				y3=y1;
				//invertdrawingorder
				vartmp=x3;
				x3=x1;
				x1=tmp;
			}
		}
		return{x1:x1,x2:x2,x3:x3,y1:y1,y2:y2,y3:y3};
	},

	drawTitle:function(pt,vm,ctx){
		vartitle=vm.title;
		varlength=title.length;
		vartitleFontSize,titleSpacing,i;

		if(length){
			varrtlHelper=getRtlHelper(vm.rtl,vm.x,vm.width);

			pt.x=getAlignedX(vm,vm._titleAlign);

			ctx.textAlign=rtlHelper.textAlign(vm._titleAlign);
			ctx.textBaseline='middle';

			titleFontSize=vm.titleFontSize;
			titleSpacing=vm.titleSpacing;

			ctx.fillStyle=vm.titleFontColor;
			ctx.font=helpers$1.fontString(titleFontSize,vm._titleFontStyle,vm._titleFontFamily);

			for(i=0;i<length;++i){
				ctx.fillText(title[i],rtlHelper.x(pt.x),pt.y+titleFontSize/2);
				pt.y+=titleFontSize+titleSpacing;//LineHeightandspacing

				if(i+1===length){
					pt.y+=vm.titleMarginBottom-titleSpacing;//IfLast,addmargin,removespacing
				}
			}
		}
	},

	drawBody:function(pt,vm,ctx){
		varbodyFontSize=vm.bodyFontSize;
		varbodySpacing=vm.bodySpacing;
		varbodyAlign=vm._bodyAlign;
		varbody=vm.body;
		vardrawColorBoxes=vm.displayColors;
		varxLinePadding=0;
		varcolorX=drawColorBoxes?getAlignedX(vm,'left'):0;

		varrtlHelper=getRtlHelper(vm.rtl,vm.x,vm.width);

		varfillLineOfText=function(line){
			ctx.fillText(line,rtlHelper.x(pt.x+xLinePadding),pt.y+bodyFontSize/2);
			pt.y+=bodyFontSize+bodySpacing;
		};

		varbodyItem,textColor,labelColors,lines,i,j,ilen,jlen;
		varbodyAlignForCalculation=rtlHelper.textAlign(bodyAlign);

		ctx.textAlign=bodyAlign;
		ctx.textBaseline='middle';
		ctx.font=helpers$1.fontString(bodyFontSize,vm._bodyFontStyle,vm._bodyFontFamily);

		pt.x=getAlignedX(vm,bodyAlignForCalculation);

		//Beforebodylines
		ctx.fillStyle=vm.bodyFontColor;
		helpers$1.each(vm.beforeBody,fillLineOfText);

		xLinePadding=drawColorBoxes&&bodyAlignForCalculation!=='right'
			?bodyAlign==='center'?(bodyFontSize/2+1):(bodyFontSize+2)
			:0;

		//Drawbodylinesnow
		for(i=0,ilen=body.length;i<ilen;++i){
			bodyItem=body[i];
			textColor=vm.labelTextColors[i];
			labelColors=vm.labelColors[i];

			ctx.fillStyle=textColor;
			helpers$1.each(bodyItem.before,fillLineOfText);

			lines=bodyItem.lines;
			for(j=0,jlen=lines.length;j<jlen;++j){
				//DrawLegend-likeboxesifneeded
				if(drawColorBoxes){
					varrtlColorX=rtlHelper.x(colorX);

					//Fillawhiterectsothatcoloursmergenicelyiftheopacityis<1
					ctx.fillStyle=vm.legendColorBackground;
					ctx.fillRect(rtlHelper.leftForLtr(rtlColorX,bodyFontSize),pt.y,bodyFontSize,bodyFontSize);

					//Border
					ctx.lineWidth=1;
					ctx.strokeStyle=labelColors.borderColor;
					ctx.strokeRect(rtlHelper.leftForLtr(rtlColorX,bodyFontSize),pt.y,bodyFontSize,bodyFontSize);

					//Innersquare
					ctx.fillStyle=labelColors.backgroundColor;
					ctx.fillRect(rtlHelper.leftForLtr(rtlHelper.xPlus(rtlColorX,1),bodyFontSize-2),pt.y+1,bodyFontSize-2,bodyFontSize-2);
					ctx.fillStyle=textColor;
				}

				fillLineOfText(lines[j]);
			}

			helpers$1.each(bodyItem.after,fillLineOfText);
		}

		//Resetbackto0forafterbody
		xLinePadding=0;

		//Afterbodylines
		helpers$1.each(vm.afterBody,fillLineOfText);
		pt.y-=bodySpacing;//Removelastbodyspacing
	},

	drawFooter:function(pt,vm,ctx){
		varfooter=vm.footer;
		varlength=footer.length;
		varfooterFontSize,i;

		if(length){
			varrtlHelper=getRtlHelper(vm.rtl,vm.x,vm.width);

			pt.x=getAlignedX(vm,vm._footerAlign);
			pt.y+=vm.footerMarginTop;

			ctx.textAlign=rtlHelper.textAlign(vm._footerAlign);
			ctx.textBaseline='middle';

			footerFontSize=vm.footerFontSize;

			ctx.fillStyle=vm.footerFontColor;
			ctx.font=helpers$1.fontString(footerFontSize,vm._footerFontStyle,vm._footerFontFamily);

			for(i=0;i<length;++i){
				ctx.fillText(footer[i],rtlHelper.x(pt.x),pt.y+footerFontSize/2);
				pt.y+=footerFontSize+vm.footerSpacing;
			}
		}
	},

	drawBackground:function(pt,vm,ctx,tooltipSize){
		ctx.fillStyle=vm.backgroundColor;
		ctx.strokeStyle=vm.borderColor;
		ctx.lineWidth=vm.borderWidth;
		varxAlign=vm.xAlign;
		varyAlign=vm.yAlign;
		varx=pt.x;
		vary=pt.y;
		varwidth=tooltipSize.width;
		varheight=tooltipSize.height;
		varradius=vm.cornerRadius;

		ctx.beginPath();
		ctx.moveTo(x+radius,y);
		if(yAlign==='top'){
			this.drawCaret(pt,tooltipSize);
		}
		ctx.lineTo(x+width-radius,y);
		ctx.quadraticCurveTo(x+width,y,x+width,y+radius);
		if(yAlign==='center'&&xAlign==='right'){
			this.drawCaret(pt,tooltipSize);
		}
		ctx.lineTo(x+width,y+height-radius);
		ctx.quadraticCurveTo(x+width,y+height,x+width-radius,y+height);
		if(yAlign==='bottom'){
			this.drawCaret(pt,tooltipSize);
		}
		ctx.lineTo(x+radius,y+height);
		ctx.quadraticCurveTo(x,y+height,x,y+height-radius);
		if(yAlign==='center'&&xAlign==='left'){
			this.drawCaret(pt,tooltipSize);
		}
		ctx.lineTo(x,y+radius);
		ctx.quadraticCurveTo(x,y,x+radius,y);
		ctx.closePath();

		ctx.fill();

		if(vm.borderWidth>0){
			ctx.stroke();
		}
	},

	draw:function(){
		varctx=this._chart.ctx;
		varvm=this._view;

		if(vm.opacity===0){
			return;
		}

		vartooltipSize={
			width:vm.width,
			height:vm.height
		};
		varpt={
			x:vm.x,
			y:vm.y
		};

		//IE11/Edgedoesnotlikeverysmallopacities,sosnapto0
		varopacity=Math.abs(vm.opacity<1e-3)?0:vm.opacity;

		//Truthy/falseyvalueforemptytooltip
		varhasTooltipContent=vm.title.length||vm.beforeBody.length||vm.body.length||vm.afterBody.length||vm.footer.length;

		if(this._options.enabled&&hasTooltipContent){
			ctx.save();
			ctx.globalAlpha=opacity;

			//DrawBackground
			this.drawBackground(pt,vm,ctx,tooltipSize);

			//DrawTitle,Body,andFooter
			pt.y+=vm.yPadding;

			helpers$1.rtl.overrideTextDirection(ctx,vm.textDirection);

			//Titles
			this.drawTitle(pt,vm,ctx);

			//Body
			this.drawBody(pt,vm,ctx);

			//Footer
			this.drawFooter(pt,vm,ctx);

			helpers$1.rtl.restoreTextDirection(ctx,vm.textDirection);

			ctx.restore();
		}
	},

	/**
	*Handleanevent
	*@private
	*@param{IEvent}event-Theeventtohandle
	*@returns{boolean}trueifthetooltipchanged
	*/
	handleEvent:function(e){
		varme=this;
		varoptions=me._options;
		varchanged=false;

		me._lastActive=me._lastActive||[];

		//FindActiveElementsfortooltips
		if(e.type==='mouseout'){
			me._active=[];
		}else{
			me._active=me._chart.getElementsAtEventForMode(e,options.mode,options);
			if(options.reverse){
				me._active.reverse();
			}
		}

		//RememberLastActives
		changed=!helpers$1.arrayEquals(me._active,me._lastActive);

		//Onlyhandletargeteventontooltipchange
		if(changed){
			me._lastActive=me._active;

			if(options.enabled||options.custom){
				me._eventPosition={
					x:e.x,
					y:e.y
				};

				me.update(true);
				me.pivot();
			}
		}

		returnchanged;
	}
});

/**
 *@namespaceChart.Tooltip.positioners
 */
varpositioners_1=positioners;

varcore_tooltip=exports$4;
core_tooltip.positioners=positioners_1;

varvalueOrDefault$9=helpers$1.valueOrDefault;

core_defaults._set('global',{
	elements:{},
	events:[
		'mousemove',
		'mouseout',
		'click',
		'touchstart',
		'touchmove'
	],
	hover:{
		onHover:null,
		mode:'nearest',
		intersect:true,
		animationDuration:400
	},
	onClick:null,
	maintainAspectRatio:true,
	responsive:true,
	responsiveAnimationDuration:0
});

/**
 *Recursivelymergethegivenconfigobjectsrepresentingthe`scales`option
 *byincorporatingscaledefaultsin`xAxes`and`yAxes`arrayitems,then
 *returnsadeepcopyoftheresult,thusdoesn'talterinputs.
 */
functionmergeScaleConfig(/*configobjects...*/){
	returnhelpers$1.merge(Object.create(null),[].slice.call(arguments),{
		merger:function(key,target,source,options){
			if(key==='xAxes'||key==='yAxes'){
				varslen=source[key].length;
				vari,type,scale;

				if(!target[key]){
					target[key]=[];
				}

				for(i=0;i<slen;++i){
					scale=source[key][i];
					type=valueOrDefault$9(scale.type,key==='xAxes'?'category':'linear');

					if(i>=target[key].length){
						target[key].push({});
					}

					if(!target[key][i].type||(scale.type&&scale.type!==target[key][i].type)){
						//new/untypedscaleortypechanged:let'sapplythenewdefaults
						//thenmergesourcescaletocorrectlyoverwritethedefaults.
						helpers$1.merge(target[key][i],[core_scaleService.getScaleDefaults(type),scale]);
					}else{
						//scalestypearethesame
						helpers$1.merge(target[key][i],scale);
					}
				}
			}else{
				helpers$1._merger(key,target,source,options);
			}
		}
	});
}

/**
 *Recursivelymergethegivenconfigobjectsastherootoptionsbyhandling
 *defaultscaleoptionsforthe`scales`and`scale`properties,thenreturns
 *adeepcopyoftheresult,thusdoesn'talterinputs.
 */
functionmergeConfig(/*configobjects...*/){
	returnhelpers$1.merge(Object.create(null),[].slice.call(arguments),{
		merger:function(key,target,source,options){
			vartval=target[key]||Object.create(null);
			varsval=source[key];

			if(key==='scales'){
				//scaleconfigmergingiscomplex.Addourownfunctionhereforthat
				target[key]=mergeScaleConfig(tval,sval);
			}elseif(key==='scale'){
				//usedinpolararea&radarchartssincethereisonlyonescale
				target[key]=helpers$1.merge(tval,[core_scaleService.getScaleDefaults(sval.type),sval]);
			}else{
				helpers$1._merger(key,target,source,options);
			}
		}
	});
}

functioninitConfig(config){
	config=config||Object.create(null);

	//DoNOTusemergeConfigforthedataobjectbecausethismethodmergesarrays
	//andsowouldchangereferencestolabelsanddatasets,preventingdataupdates.
	vardata=config.data=config.data||{};
	data.datasets=data.datasets||[];
	data.labels=data.labels||[];

	config.options=mergeConfig(
		core_defaults.global,
		core_defaults[config.type],
		config.options||{});

	returnconfig;
}

functionupdateConfig(chart){
	varnewOptions=chart.options;

	helpers$1.each(chart.scales,function(scale){
		core_layouts.removeBox(chart,scale);
	});

	newOptions=mergeConfig(
		core_defaults.global,
		core_defaults[chart.config.type],
		newOptions);

	chart.options=chart.config.options=newOptions;
	chart.ensureScalesHaveIDs();
	chart.buildOrUpdateScales();

	//Tooltip
	chart.tooltip._options=newOptions.tooltips;
	chart.tooltip.initialize();
}

functionnextAvailableScaleId(axesOpts,prefix,index){
	varid;
	varhasId=function(obj){
		returnobj.id===id;
	};

	do{
		id=prefix+index++;
	}while(helpers$1.findIndex(axesOpts,hasId)>=0);

	returnid;
}

functionpositionIsHorizontal(position){
	returnposition==='top'||position==='bottom';
}

functioncompare2Level(l1,l2){
	returnfunction(a,b){
		returna[l1]===b[l1]
			?a[l2]-b[l2]
			:a[l1]-b[l1];
	};
}

varChart=function(item,config){
	this.construct(item,config);
	returnthis;
};

helpers$1.extend(Chart.prototype,/**@lendsChart*/{
	/**
	*@private
	*/
	construct:function(item,config){
		varme=this;

		config=initConfig(config);

		varcontext=platform.acquireContext(item,config);
		varcanvas=context&&context.canvas;
		varheight=canvas&&canvas.height;
		varwidth=canvas&&canvas.width;

		me.id=helpers$1.uid();
		me.ctx=context;
		me.canvas=canvas;
		me.config=config;
		me.width=width;
		me.height=height;
		me.aspectRatio=height?width/height:null;
		me.options=config.options;
		me._bufferedRender=false;
		me._layers=[];

		/**
		*Providedforbackwardcompatibility,ChartandChart.Controllerhavebeenmerged,
		*the"instance"stillneedtobedefinedsinceitmightbecalledfromplugins.
		*@propChart#chart
		*@deprecatedsinceversion2.6.0
		*@todoremoveatversion3
		*@private
		*/
		me.chart=me;
		me.controller=me;//chart.chart.controller#inception

		//Addthechartinstancetotheglobalnamespace
		Chart.instances[me.id]=me;

		//Definealiastotheconfigdata:`chart.data===chart.config.data`
		Object.defineProperty(me,'data',{
			get:function(){
				returnme.config.data;
			},
			set:function(value){
				me.config.data=value;
			}
		});

		if(!context||!canvas){
			//Thegivenitemisnotacompatiblecontext2delement,let'sreturnbeforefinalizing
			//thechartinitializationbutaftersettingbasicchart/controllerpropertiesthat
			//canhelptofigureoutthatthechartisnotvalid(e.gchart.canvas!==null);
			//https://github.com/chartjs/Chart.js/issues/2807
			console.error("Failedtocreatechart:can'tacquirecontextfromthegivenitem");
			return;
		}

		me.initialize();
		me.update();
	},

	/**
	*@private
	*/
	initialize:function(){
		varme=this;

		//Beforeinitpluginnotification
		core_plugins.notify(me,'beforeInit');

		helpers$1.retinaScale(me,me.options.devicePixelRatio);

		me.bindEvents();

		if(me.options.responsive){
			//Initialresizebeforechartdraws(mustbesilenttopreserveinitialanimations).
			me.resize(true);
		}

		me.initToolTip();

		//Afterinitpluginnotification
		core_plugins.notify(me,'afterInit');

		returnme;
	},

	clear:function(){
		helpers$1.canvas.clear(this);
		returnthis;
	},

	stop:function(){
		//Stopsanycurrentanimationloopoccurring
		core_animations.cancelAnimation(this);
		returnthis;
	},

	resize:function(silent){
		varme=this;
		varoptions=me.options;
		varcanvas=me.canvas;
		varaspectRatio=(options.maintainAspectRatio&&me.aspectRatio)||null;

		//thecanvasrenderwidthandheightwillbecastedtointegerssomakesurethat
		//thecanvasdisplaystyleusesthesameintegervaluestoavoidblurringeffect.

		//Setto0insteadofcanvas.sizebecausethesizedefaultsto300x150iftheelementiscollapsed
		varnewWidth=Math.max(0,Math.floor(helpers$1.getMaximumWidth(canvas)));
		varnewHeight=Math.max(0,Math.floor(aspectRatio?newWidth/aspectRatio:helpers$1.getMaximumHeight(canvas)));

		if(me.width===newWidth&&me.height===newHeight){
			return;
		}

		canvas.width=me.width=newWidth;
		canvas.height=me.height=newHeight;
		canvas.style.width=newWidth+'px';
		canvas.style.height=newHeight+'px';

		helpers$1.retinaScale(me,options.devicePixelRatio);

		if(!silent){
			//Notifyanypluginsabouttheresize
			varnewSize={width:newWidth,height:newHeight};
			core_plugins.notify(me,'resize',[newSize]);

			//Notifyofresize
			if(options.onResize){
				options.onResize(me,newSize);
			}

			me.stop();
			me.update({
				duration:options.responsiveAnimationDuration
			});
		}
	},

	ensureScalesHaveIDs:function(){
		varoptions=this.options;
		varscalesOptions=options.scales||{};
		varscaleOptions=options.scale;

		helpers$1.each(scalesOptions.xAxes,function(xAxisOptions,index){
			if(!xAxisOptions.id){
				xAxisOptions.id=nextAvailableScaleId(scalesOptions.xAxes,'x-axis-',index);
			}
		});

		helpers$1.each(scalesOptions.yAxes,function(yAxisOptions,index){
			if(!yAxisOptions.id){
				yAxisOptions.id=nextAvailableScaleId(scalesOptions.yAxes,'y-axis-',index);
			}
		});

		if(scaleOptions){
			scaleOptions.id=scaleOptions.id||'scale';
		}
	},

	/**
	*BuildsamapofscaleIDtoscaleobjectforfuturelookup.
	*/
	buildOrUpdateScales:function(){
		varme=this;
		varoptions=me.options;
		varscales=me.scales||{};
		varitems=[];
		varupdated=Object.keys(scales).reduce(function(obj,id){
			obj[id]=false;
			returnobj;
		},{});

		if(options.scales){
			items=items.concat(
				(options.scales.xAxes||[]).map(function(xAxisOptions){
					return{options:xAxisOptions,dtype:'category',dposition:'bottom'};
				}),
				(options.scales.yAxes||[]).map(function(yAxisOptions){
					return{options:yAxisOptions,dtype:'linear',dposition:'left'};
				})
			);
		}

		if(options.scale){
			items.push({
				options:options.scale,
				dtype:'radialLinear',
				isDefault:true,
				dposition:'chartArea'
			});
		}

		helpers$1.each(items,function(item){
			varscaleOptions=item.options;
			varid=scaleOptions.id;
			varscaleType=valueOrDefault$9(scaleOptions.type,item.dtype);

			if(positionIsHorizontal(scaleOptions.position)!==positionIsHorizontal(item.dposition)){
				scaleOptions.position=item.dposition;
			}

			updated[id]=true;
			varscale=null;
			if(idinscales&&scales[id].type===scaleType){
				scale=scales[id];
				scale.options=scaleOptions;
				scale.ctx=me.ctx;
				scale.chart=me;
			}else{
				varscaleClass=core_scaleService.getScaleConstructor(scaleType);
				if(!scaleClass){
					return;
				}
				scale=newscaleClass({
					id:id,
					type:scaleType,
					options:scaleOptions,
					ctx:me.ctx,
					chart:me
				});
				scales[scale.id]=scale;
			}

			scale.mergeTicksOptions();

			//TODO(SB):Ithinkweshouldbeabletoremovethiscustomcase(options.scale)
			//andconsideritasaregularscalepartofthe"scales""maponly!Thiswould
			//makethelogiceasierandremovesomeuseless?customcode.
			if(item.isDefault){
				me.scale=scale;
			}
		});
		//clearupdiscardedscales
		helpers$1.each(updated,function(hasUpdated,id){
			if(!hasUpdated){
				deletescales[id];
			}
		});

		me.scales=scales;

		core_scaleService.addScalesToLayout(this);
	},

	buildOrUpdateControllers:function(){
		varme=this;
		varnewControllers=[];
		vardatasets=me.data.datasets;
		vari,ilen;

		for(i=0,ilen=datasets.length;i<ilen;i++){
			vardataset=datasets[i];
			varmeta=me.getDatasetMeta(i);
			vartype=dataset.type||me.config.type;

			if(meta.type&&meta.type!==type){
				me.destroyDatasetMeta(i);
				meta=me.getDatasetMeta(i);
			}
			meta.type=type;
			meta.order=dataset.order||0;
			meta.index=i;

			if(meta.controller){
				meta.controller.updateIndex(i);
				meta.controller.linkScales();
			}else{
				varControllerClass=controllers[meta.type];
				if(ControllerClass===undefined){
					thrownewError('"'+meta.type+'"isnotacharttype.');
				}

				meta.controller=newControllerClass(me,i);
				newControllers.push(meta.controller);
			}
		}

		returnnewControllers;
	},

	/**
	*Resettheelementsofalldatasets
	*@private
	*/
	resetElements:function(){
		varme=this;
		helpers$1.each(me.data.datasets,function(dataset,datasetIndex){
			me.getDatasetMeta(datasetIndex).controller.reset();
		},me);
	},

	/**
	*Resetsthechartbacktoit'sstatebeforetheinitialanimation
	*/
	reset:function(){
		this.resetElements();
		this.tooltip.initialize();
	},

	update:function(config){
		varme=this;
		vari,ilen;

		if(!config||typeofconfig!=='object'){
			//backwardscompatibility
			config={
				duration:config,
				lazy:arguments[1]
			};
		}

		updateConfig(me);

		//pluginsoptionsreferencesmighthavechange,let'sinvalidatethecache
		//https://github.com/chartjs/Chart.js/issues/5111#issuecomment-355934167
		core_plugins._invalidate(me);

		if(core_plugins.notify(me,'beforeUpdate')===false){
			return;
		}

		//Incasetheentiredataobjectchanged
		me.tooltip._data=me.data;

		//Makesuredatasetcontrollersareupdatedandnewcontrollersarereset
		varnewControllers=me.buildOrUpdateControllers();

		//Makesurealldatasetcontrollershavecorrectmetadatacounts
		for(i=0,ilen=me.data.datasets.length;i<ilen;i++){
			me.getDatasetMeta(i).controller.buildOrUpdateElements();
		}

		me.updateLayout();

		//Canonlyresetthenewcontrollersafterthescaleshavebeenupdated
		if(me.options.animation&&me.options.animation.duration){
			helpers$1.each(newControllers,function(controller){
				controller.reset();
			});
		}

		me.updateDatasets();

		//Needtoresettooltipincaseitisdisplayedwithelementsthatareremoved
		//afterupdate.
		me.tooltip.initialize();

		//Lastactivecontainsitemsthatwerepreviouslyinthetooltip.
		//Whenweresetthetooltip,weneedtoclearit
		me.lastActive=[];

		//Dothisbeforerendersothatanypluginsthatneedfinalscaleupdatescanuseit
		core_plugins.notify(me,'afterUpdate');

		me._layers.sort(compare2Level('z','_idx'));

		if(me._bufferedRender){
			me._bufferedRequest={
				duration:config.duration,
				easing:config.easing,
				lazy:config.lazy
			};
		}else{
			me.render(config);
		}
	},

	/**
	*Updatesthechartlayoutunlessapluginreturns`false`tothe`beforeLayout`
	*hook,inwhichcase,pluginswillnotbecalledon`afterLayout`.
	*@private
	*/
	updateLayout:function(){
		varme=this;

		if(core_plugins.notify(me,'beforeLayout')===false){
			return;
		}

		core_layouts.update(this,this.width,this.height);

		me._layers=[];
		helpers$1.each(me.boxes,function(box){
			//_configureiscalledtwice,onceincore.scale.updateandoncehere.
			//Heretheboxesarefullyupdatedandattheirfinalpositions.
			if(box._configure){
				box._configure();
			}
			me._layers.push.apply(me._layers,box._layers());
		},me);

		me._layers.forEach(function(item,index){
			item._idx=index;
		});

		/**
		*Providedforbackwardcompatibility,use`afterLayout`instead.
		*@methodIPlugin#afterScaleUpdate
		*@deprecatedsinceversion2.5.0
		*@todoremoveatversion3
		*@private
		*/
		core_plugins.notify(me,'afterScaleUpdate');
		core_plugins.notify(me,'afterLayout');
	},

	/**
	*Updatesalldatasetsunlessapluginreturns`false`tothe`beforeDatasetsUpdate`
	*hook,inwhichcase,pluginswillnotbecalledon`afterDatasetsUpdate`.
	*@private
	*/
	updateDatasets:function(){
		varme=this;

		if(core_plugins.notify(me,'beforeDatasetsUpdate')===false){
			return;
		}

		for(vari=0,ilen=me.data.datasets.length;i<ilen;++i){
			me.updateDataset(i);
		}

		core_plugins.notify(me,'afterDatasetsUpdate');
	},

	/**
	*Updatesdatasetatindexunlessapluginreturns`false`tothe`beforeDatasetUpdate`
	*hook,inwhichcase,pluginswillnotbecalledon`afterDatasetUpdate`.
	*@private
	*/
	updateDataset:function(index){
		varme=this;
		varmeta=me.getDatasetMeta(index);
		varargs={
			meta:meta,
			index:index
		};

		if(core_plugins.notify(me,'beforeDatasetUpdate',[args])===false){
			return;
		}

		meta.controller._update();

		core_plugins.notify(me,'afterDatasetUpdate',[args]);
	},

	render:function(config){
		varme=this;

		if(!config||typeofconfig!=='object'){
			//backwardscompatibility
			config={
				duration:config,
				lazy:arguments[1]
			};
		}

		varanimationOptions=me.options.animation;
		varduration=valueOrDefault$9(config.duration,animationOptions&&animationOptions.duration);
		varlazy=config.lazy;

		if(core_plugins.notify(me,'beforeRender')===false){
			return;
		}

		varonComplete=function(animation){
			core_plugins.notify(me,'afterRender');
			helpers$1.callback(animationOptions&&animationOptions.onComplete,[animation],me);
		};

		if(animationOptions&&duration){
			varanimation=newcore_animation({
				numSteps:duration/16.66,//60fps
				easing:config.easing||animationOptions.easing,

				render:function(chart,animationObject){
					vareasingFunction=helpers$1.easing.effects[animationObject.easing];
					varcurrentStep=animationObject.currentStep;
					varstepDecimal=currentStep/animationObject.numSteps;

					chart.draw(easingFunction(stepDecimal),stepDecimal,currentStep);
				},

				onAnimationProgress:animationOptions.onProgress,
				onAnimationComplete:onComplete
			});

			core_animations.addAnimation(me,animation,duration,lazy);
		}else{
			me.draw();

			//Seehttps://github.com/chartjs/Chart.js/issues/3781
			onComplete(newcore_animation({numSteps:0,chart:me}));
		}

		returnme;
	},

	draw:function(easingValue){
		varme=this;
		vari,layers;

		me.clear();

		if(helpers$1.isNullOrUndef(easingValue)){
			easingValue=1;
		}

		me.transition(easingValue);

		if(me.width<=0||me.height<=0){
			return;
		}

		if(core_plugins.notify(me,'beforeDraw',[easingValue])===false){
			return;
		}

		//Becauseofpluginhooks(before/afterDatasetsDraw),datasetscan't
		//currentlybepartoflayers.Instead,wedraw
		//layers<=0before(default,backwardcompat),andtherestafter
		layers=me._layers;
		for(i=0;i<layers.length&&layers[i].z<=0;++i){
			layers[i].draw(me.chartArea);
		}

		me.drawDatasets(easingValue);

		//Restoflayers
		for(;i<layers.length;++i){
			layers[i].draw(me.chartArea);
		}

		me._drawTooltip(easingValue);

		core_plugins.notify(me,'afterDraw',[easingValue]);
	},

	/**
	*@private
	*/
	transition:function(easingValue){
		varme=this;

		for(vari=0,ilen=(me.data.datasets||[]).length;i<ilen;++i){
			if(me.isDatasetVisible(i)){
				me.getDatasetMeta(i).controller.transition(easingValue);
			}
		}

		me.tooltip.transition(easingValue);
	},

	/**
	*@private
	*/
	_getSortedDatasetMetas:function(filterVisible){
		varme=this;
		vardatasets=me.data.datasets||[];
		varresult=[];
		vari,ilen;

		for(i=0,ilen=datasets.length;i<ilen;++i){
			if(!filterVisible||me.isDatasetVisible(i)){
				result.push(me.getDatasetMeta(i));
			}
		}

		result.sort(compare2Level('order','index'));

		returnresult;
	},

	/**
	*@private
	*/
	_getSortedVisibleDatasetMetas:function(){
		returnthis._getSortedDatasetMetas(true);
	},

	/**
	*Drawsalldatasetsunlessapluginreturns`false`tothe`beforeDatasetsDraw`
	*hook,inwhichcase,pluginswillnotbecalledon`afterDatasetsDraw`.
	*@private
	*/
	drawDatasets:function(easingValue){
		varme=this;
		varmetasets,i;

		if(core_plugins.notify(me,'beforeDatasetsDraw',[easingValue])===false){
			return;
		}

		metasets=me._getSortedVisibleDatasetMetas();
		for(i=metasets.length-1;i>=0;--i){
			me.drawDataset(metasets[i],easingValue);
		}

		core_plugins.notify(me,'afterDatasetsDraw',[easingValue]);
	},

	/**
	*Drawsdatasetatindexunlessapluginreturns`false`tothe`beforeDatasetDraw`
	*hook,inwhichcase,pluginswillnotbecalledon`afterDatasetDraw`.
	*@private
	*/
	drawDataset:function(meta,easingValue){
		varme=this;
		varargs={
			meta:meta,
			index:meta.index,
			easingValue:easingValue
		};

		if(core_plugins.notify(me,'beforeDatasetDraw',[args])===false){
			return;
		}

		meta.controller.draw(easingValue);

		core_plugins.notify(me,'afterDatasetDraw',[args]);
	},

	/**
	*Drawstooltipunlessapluginreturns`false`tothe`beforeTooltipDraw`
	*hook,inwhichcase,pluginswillnotbecalledon`afterTooltipDraw`.
	*@private
	*/
	_drawTooltip:function(easingValue){
		varme=this;
		vartooltip=me.tooltip;
		varargs={
			tooltip:tooltip,
			easingValue:easingValue
		};

		if(core_plugins.notify(me,'beforeTooltipDraw',[args])===false){
			return;
		}

		tooltip.draw();

		core_plugins.notify(me,'afterTooltipDraw',[args]);
	},

	/**
	*Getthesingleelementthatwasclickedon
	*@returnAnobjectcontainingthedatasetindexandelementindexofthematchingelement.Alsocontainstherectanglethatwasdraw
	*/
	getElementAtEvent:function(e){
		returncore_interaction.modes.single(this,e);
	},

	getElementsAtEvent:function(e){
		returncore_interaction.modes.label(this,e,{intersect:true});
	},

	getElementsAtXAxis:function(e){
		returncore_interaction.modes['x-axis'](this,e,{intersect:true});
	},

	getElementsAtEventForMode:function(e,mode,options){
		varmethod=core_interaction.modes[mode];
		if(typeofmethod==='function'){
			returnmethod(this,e,options);
		}

		return[];
	},

	getDatasetAtEvent:function(e){
		returncore_interaction.modes.dataset(this,e,{intersect:true});
	},

	getDatasetMeta:function(datasetIndex){
		varme=this;
		vardataset=me.data.datasets[datasetIndex];
		if(!dataset._meta){
			dataset._meta={};
		}

		varmeta=dataset._meta[me.id];
		if(!meta){
			meta=dataset._meta[me.id]={
				type:null,
				data:[],
				dataset:null,
				controller:null,
				hidden:null,			//SeeisDatasetVisible()comment
				xAxisID:null,
				yAxisID:null,
				order:dataset.order||0,
				index:datasetIndex
			};
		}

		returnmeta;
	},

	getVisibleDatasetCount:function(){
		varcount=0;
		for(vari=0,ilen=this.data.datasets.length;i<ilen;++i){
			if(this.isDatasetVisible(i)){
				count++;
			}
		}
		returncount;
	},

	isDatasetVisible:function(datasetIndex){
		varmeta=this.getDatasetMeta(datasetIndex);

		//meta.hiddenisaperchartdatasethiddenflagoverridewith3states:iftrueorfalse,
		//thedataset.hiddenvalueisignored,elseifnull,thedatasethiddenstateisreturned.
		returntypeofmeta.hidden==='boolean'?!meta.hidden:!this.data.datasets[datasetIndex].hidden;
	},

	generateLegend:function(){
		returnthis.options.legendCallback(this);
	},

	/**
	*@private
	*/
	destroyDatasetMeta:function(datasetIndex){
		varid=this.id;
		vardataset=this.data.datasets[datasetIndex];
		varmeta=dataset._meta&&dataset._meta[id];

		if(meta){
			meta.controller.destroy();
			deletedataset._meta[id];
		}
	},

	destroy:function(){
		varme=this;
		varcanvas=me.canvas;
		vari,ilen;

		me.stop();

		//datasetcontrollersneedtocleanupassociateddata
		for(i=0,ilen=me.data.datasets.length;i<ilen;++i){
			me.destroyDatasetMeta(i);
		}

		if(canvas){
			me.unbindEvents();
			helpers$1.canvas.clear(me);
			platform.releaseContext(me.ctx);
			me.canvas=null;
			me.ctx=null;
		}

		core_plugins.notify(me,'destroy');

		deleteChart.instances[me.id];
	},

	toBase64Image:function(){
		returnthis.canvas.toDataURL.apply(this.canvas,arguments);
	},

	initToolTip:function(){
		varme=this;
		me.tooltip=newcore_tooltip({
			_chart:me,
			_chartInstance:me,//deprecated,backwardcompatibility
			_data:me.data,
			_options:me.options.tooltips
		},me);
	},

	/**
	*@private
	*/
	bindEvents:function(){
		varme=this;
		varlisteners=me._listeners={};
		varlistener=function(){
			me.eventHandler.apply(me,arguments);
		};

		helpers$1.each(me.options.events,function(type){
			platform.addEventListener(me,type,listener);
			listeners[type]=listener;
		});

		//Elementsusedtodetectsizechangeshouldnotbeinjectedfornonresponsivecharts.
		//Seehttps://github.com/chartjs/Chart.js/issues/2210
		if(me.options.responsive){
			listener=function(){
				me.resize();
			};

			platform.addEventListener(me,'resize',listener);
			listeners.resize=listener;
		}
	},

	/**
	*@private
	*/
	unbindEvents:function(){
		varme=this;
		varlisteners=me._listeners;
		if(!listeners){
			return;
		}

		deleteme._listeners;
		helpers$1.each(listeners,function(listener,type){
			platform.removeEventListener(me,type,listener);
		});
	},

	updateHoverStyle:function(elements,mode,enabled){
		varprefix=enabled?'set':'remove';
		varelement,i,ilen;

		for(i=0,ilen=elements.length;i<ilen;++i){
			element=elements[i];
			if(element){
				this.getDatasetMeta(element._datasetIndex).controller[prefix+'HoverStyle'](element);
			}
		}

		if(mode==='dataset'){
			this.getDatasetMeta(elements[0]._datasetIndex).controller['_'+prefix+'DatasetHoverStyle']();
		}
	},

	/**
	*@private
	*/
	eventHandler:function(e){
		varme=this;
		vartooltip=me.tooltip;

		if(core_plugins.notify(me,'beforeEvent',[e])===false){
			return;
		}

		//Bufferanyupdatecallssothatrendersdonotoccur
		me._bufferedRender=true;
		me._bufferedRequest=null;

		varchanged=me.handleEvent(e);
		//forsmoothtooltipanimationsissue#4989
		//thetooltipshouldbethesourceofchange
		//Animationcheckworkaround:
		//tooltip._startwillbenullwhentooltipisn'tanimating
		if(tooltip){
			changed=tooltip._start
				?tooltip.handleEvent(e)
				:changed|tooltip.handleEvent(e);
		}

		core_plugins.notify(me,'afterEvent',[e]);

		varbufferedRequest=me._bufferedRequest;
		if(bufferedRequest){
			//Ifwehaveanupdatethatwastriggered,weneedtodoanormalrender
			me.render(bufferedRequest);
		}elseif(changed&&!me.animating){
			//Ifentering,leaving,orchangingelements,animatethechangeviapivot
			me.stop();

			//Weonlyneedtorenderatthispoint.Updatingwillcausescalestobe
			//recomputedgeneratingflicker&usingmorememorythannecessary.
			me.render({
				duration:me.options.hover.animationDuration,
				lazy:true
			});
		}

		me._bufferedRender=false;
		me._bufferedRequest=null;

		returnme;
	},

	/**
	*Handleanevent
	*@private
	*@param{IEvent}eventtheeventtohandle
	*@return{boolean}trueifthechartneedstore-render
	*/
	handleEvent:function(e){
		varme=this;
		varoptions=me.options||{};
		varhoverOptions=options.hover;
		varchanged=false;

		me.lastActive=me.lastActive||[];

		//FindActiveElementsforhoverandtooltips
		if(e.type==='mouseout'){
			me.active=[];
		}else{
			me.active=me.getElementsAtEventForMode(e,hoverOptions.mode,hoverOptions);
		}

		//InvokeonHoverhook
		//Needtocallwithnativeeventheretonotbreakbackwardscompatibility
		helpers$1.callback(options.onHover||options.hover.onHover,[e.native,me.active],me);

		if(e.type==='mouseup'||e.type==='click'){
			if(options.onClick){
				//Usee.nativehereforbackwardscompatibility
				options.onClick.call(me,e.native,me.active);
			}
		}

		//Removestylingforlastactive(evenifitmaystillbeactive)
		if(me.lastActive.length){
			me.updateHoverStyle(me.lastActive,hoverOptions.mode,false);
		}

		//Builtinhoverstyling
		if(me.active.length&&hoverOptions.mode){
			me.updateHoverStyle(me.active,hoverOptions.mode,true);
		}

		changed=!helpers$1.arrayEquals(me.active,me.lastActive);

		//RememberLastActives
		me.lastActive=me.active;

		returnchanged;
	}
});

/**
 *NOTE(SB)Weactuallydon'tusethiscontaineranymorebutweneedtokeepit
 *forbackwardcompatibility.Though,itcanstillbeusefulforpluginsthat
 *wouldneedtoworkonmultiplecharts?!
 */
Chart.instances={};

varcore_controller=Chart;

//DEPRECATIONS

/**
 *Providedforbackwardcompatibility,useChartinstead.
 *@classChart.Controller
 *@deprecatedsinceversion2.6
 *@todoremoveatversion3
 *@private
 */
Chart.Controller=Chart;

/**
 *Providedforbackwardcompatibility,notavailableanymore.
 *@namespaceChart
 *@deprecatedsinceversion2.8
 *@todoremoveatversion3
 *@private
 */
Chart.types={};

/**
 *Providedforbackwardcompatibility,notavailableanymore.
 *@namespaceChart.helpers.configMerge
 *@deprecatedsinceversion2.8.0
 *@todoremoveatversion3
 *@private
 */
helpers$1.configMerge=mergeConfig;

/**
 *Providedforbackwardcompatibility,notavailableanymore.
 *@namespaceChart.helpers.scaleMerge
 *@deprecatedsinceversion2.8.0
 *@todoremoveatversion3
 *@private
 */
helpers$1.scaleMerge=mergeScaleConfig;

varcore_helpers=function(){

	//--Basicjsutilitymethods

	helpers$1.where=function(collection,filterCallback){
		if(helpers$1.isArray(collection)&&Array.prototype.filter){
			returncollection.filter(filterCallback);
		}
		varfiltered=[];

		helpers$1.each(collection,function(item){
			if(filterCallback(item)){
				filtered.push(item);
			}
		});

		returnfiltered;
	};
	helpers$1.findIndex=Array.prototype.findIndex?
		function(array,callback,scope){
			returnarray.findIndex(callback,scope);
		}:
		function(array,callback,scope){
			scope=scope===undefined?array:scope;
			for(vari=0,ilen=array.length;i<ilen;++i){
				if(callback.call(scope,array[i],i,array)){
					returni;
				}
			}
			return-1;
		};
	helpers$1.findNextWhere=function(arrayToSearch,filterCallback,startIndex){
		//Defaulttostartofthearray
		if(helpers$1.isNullOrUndef(startIndex)){
			startIndex=-1;
		}
		for(vari=startIndex+1;i<arrayToSearch.length;i++){
			varcurrentItem=arrayToSearch[i];
			if(filterCallback(currentItem)){
				returncurrentItem;
			}
		}
	};
	helpers$1.findPreviousWhere=function(arrayToSearch,filterCallback,startIndex){
		//Defaulttoendofthearray
		if(helpers$1.isNullOrUndef(startIndex)){
			startIndex=arrayToSearch.length;
		}
		for(vari=startIndex-1;i>=0;i--){
			varcurrentItem=arrayToSearch[i];
			if(filterCallback(currentItem)){
				returncurrentItem;
			}
		}
	};

	//--Mathmethods
	helpers$1.isNumber=function(n){
		return!isNaN(parseFloat(n))&&isFinite(n);
	};
	helpers$1.almostEquals=function(x,y,epsilon){
		returnMath.abs(x-y)<epsilon;
	};
	helpers$1.almostWhole=function(x,epsilon){
		varrounded=Math.round(x);
		return((rounded-epsilon)<=x)&&((rounded+epsilon)>=x);
	};
	helpers$1.max=function(array){
		returnarray.reduce(function(max,value){
			if(!isNaN(value)){
				returnMath.max(max,value);
			}
			returnmax;
		},Number.NEGATIVE_INFINITY);
	};
	helpers$1.min=function(array){
		returnarray.reduce(function(min,value){
			if(!isNaN(value)){
				returnMath.min(min,value);
			}
			returnmin;
		},Number.POSITIVE_INFINITY);
	};
	helpers$1.sign=Math.sign?
		function(x){
			returnMath.sign(x);
		}:
		function(x){
			x=+x;//converttoanumber
			if(x===0||isNaN(x)){
				returnx;
			}
			returnx>0?1:-1;
		};
	helpers$1.toRadians=function(degrees){
		returndegrees*(Math.PI/180);
	};
	helpers$1.toDegrees=function(radians){
		returnradians*(180/Math.PI);
	};

	/**
	*Returnsthenumberofdecimalplaces
	*i.e.thenumberofdigitsafterthedecimalpoint,ofthevalueofthisNumber.
	*@param{number}x-Anumber.
	*@returns{number}Thenumberofdecimalplaces.
	*@private
	*/
	helpers$1._decimalPlaces=function(x){
		if(!helpers$1.isFinite(x)){
			return;
		}
		vare=1;
		varp=0;
		while(Math.round(x*e)/e!==x){
			e*=10;
			p++;
		}
		returnp;
	};

	//Getstheanglefromverticaluprighttothepointaboutacentre.
	helpers$1.getAngleFromPoint=function(centrePoint,anglePoint){
		vardistanceFromXCenter=anglePoint.x-centrePoint.x;
		vardistanceFromYCenter=anglePoint.y-centrePoint.y;
		varradialDistanceFromCenter=Math.sqrt(distanceFromXCenter*distanceFromXCenter+distanceFromYCenter*distanceFromYCenter);

		varangle=Math.atan2(distanceFromYCenter,distanceFromXCenter);

		if(angle<(-0.5*Math.PI)){
			angle+=2.0*Math.PI;//makesurethereturnedangleisintherangeof(-PI/2,3PI/2]
		}

		return{
			angle:angle,
			distance:radialDistanceFromCenter
		};
	};
	helpers$1.distanceBetweenPoints=function(pt1,pt2){
		returnMath.sqrt(Math.pow(pt2.x-pt1.x,2)+Math.pow(pt2.y-pt1.y,2));
	};

	/**
	*Providedforbackwardcompatibility,notavailableanymore
	*@functionChart.helpers.aliasPixel
	*@deprecatedsinceversion2.8.0
	*@todoremoveatversion3
	*/
	helpers$1.aliasPixel=function(pixelWidth){
		return(pixelWidth%2===0)?0:0.5;
	};

	/**
	*Returnsthealignedpixelvaluetoavoidanti-aliasingblur
	*@param{Chart}chart-Thechartinstance.
	*@param{number}pixel-Apixelvalue.
	*@param{number}width-Thewidthoftheelement.
	*@returns{number}Thealignedpixelvalue.
	*@private
	*/
	helpers$1._alignPixel=function(chart,pixel,width){
		vardevicePixelRatio=chart.currentDevicePixelRatio;
		varhalfWidth=width/2;
		returnMath.round((pixel-halfWidth)*devicePixelRatio)/devicePixelRatio+halfWidth;
	};

	helpers$1.splineCurve=function(firstPoint,middlePoint,afterPoint,t){
		//PropstoRobSpenceratscaledinnovationforhispostonspliningbetweenpoints
		//http://scaledinnovation.com/analytics/splines/aboutSplines.html

		//Thisfunctionmustalsorespect"skipped"points

		varprevious=firstPoint.skip?middlePoint:firstPoint;
		varcurrent=middlePoint;
		varnext=afterPoint.skip?middlePoint:afterPoint;

		vard01=Math.sqrt(Math.pow(current.x-previous.x,2)+Math.pow(current.y-previous.y,2));
		vard12=Math.sqrt(Math.pow(next.x-current.x,2)+Math.pow(next.y-current.y,2));

		vars01=d01/(d01+d12);
		vars12=d12/(d01+d12);

		//Ifallpointsarethesame,s01&s02willbeinf
		s01=isNaN(s01)?0:s01;
		s12=isNaN(s12)?0:s12;

		varfa=t*s01;//scalingfactorfortriangleTa
		varfb=t*s12;

		return{
			previous:{
				x:current.x-fa*(next.x-previous.x),
				y:current.y-fa*(next.y-previous.y)
			},
			next:{
				x:current.x+fb*(next.x-previous.x),
				y:current.y+fb*(next.y-previous.y)
			}
		};
	};
	helpers$1.EPSILON=Number.EPSILON||1e-14;
	helpers$1.splineCurveMonotone=function(points){
		//ThisfunctioncalculatesBéziercontrolpointsinasimilarwaythan|splineCurve|,
		//butpreservesmonotonicityoftheprovideddataandensuresnolocalextremumsareadded
		//betweenthedatasetdiscretepointsduetotheinterpolation.
		//See:https://en.wikipedia.org/wiki/Monotone_cubic_interpolation

		varpointsWithTangents=(points||[]).map(function(point){
			return{
				model:point._model,
				deltaK:0,
				mK:0
			};
		});

		//Calculateslopes(deltaK)andinitializetangents(mK)
		varpointsLen=pointsWithTangents.length;
		vari,pointBefore,pointCurrent,pointAfter;
		for(i=0;i<pointsLen;++i){
			pointCurrent=pointsWithTangents[i];
			if(pointCurrent.model.skip){
				continue;
			}

			pointBefore=i>0?pointsWithTangents[i-1]:null;
			pointAfter=i<pointsLen-1?pointsWithTangents[i+1]:null;
			if(pointAfter&&!pointAfter.model.skip){
				varslopeDeltaX=(pointAfter.model.x-pointCurrent.model.x);

				//Inthecaseoftwopointsthatappearatthesamexpixel,slopeDeltaXis0
				pointCurrent.deltaK=slopeDeltaX!==0?(pointAfter.model.y-pointCurrent.model.y)/slopeDeltaX:0;
			}

			if(!pointBefore||pointBefore.model.skip){
				pointCurrent.mK=pointCurrent.deltaK;
			}elseif(!pointAfter||pointAfter.model.skip){
				pointCurrent.mK=pointBefore.deltaK;
			}elseif(this.sign(pointBefore.deltaK)!==this.sign(pointCurrent.deltaK)){
				pointCurrent.mK=0;
			}else{
				pointCurrent.mK=(pointBefore.deltaK+pointCurrent.deltaK)/2;
			}
		}

		//Adjusttangentstoensuremonotonicproperties
		varalphaK,betaK,tauK,squaredMagnitude;
		for(i=0;i<pointsLen-1;++i){
			pointCurrent=pointsWithTangents[i];
			pointAfter=pointsWithTangents[i+1];
			if(pointCurrent.model.skip||pointAfter.model.skip){
				continue;
			}

			if(helpers$1.almostEquals(pointCurrent.deltaK,0,this.EPSILON)){
				pointCurrent.mK=pointAfter.mK=0;
				continue;
			}

			alphaK=pointCurrent.mK/pointCurrent.deltaK;
			betaK=pointAfter.mK/pointCurrent.deltaK;
			squaredMagnitude=Math.pow(alphaK,2)+Math.pow(betaK,2);
			if(squaredMagnitude<=9){
				continue;
			}

			tauK=3/Math.sqrt(squaredMagnitude);
			pointCurrent.mK=alphaK*tauK*pointCurrent.deltaK;
			pointAfter.mK=betaK*tauK*pointCurrent.deltaK;
		}

		//Computecontrolpoints
		vardeltaX;
		for(i=0;i<pointsLen;++i){
			pointCurrent=pointsWithTangents[i];
			if(pointCurrent.model.skip){
				continue;
			}

			pointBefore=i>0?pointsWithTangents[i-1]:null;
			pointAfter=i<pointsLen-1?pointsWithTangents[i+1]:null;
			if(pointBefore&&!pointBefore.model.skip){
				deltaX=(pointCurrent.model.x-pointBefore.model.x)/3;
				pointCurrent.model.controlPointPreviousX=pointCurrent.model.x-deltaX;
				pointCurrent.model.controlPointPreviousY=pointCurrent.model.y-deltaX*pointCurrent.mK;
			}
			if(pointAfter&&!pointAfter.model.skip){
				deltaX=(pointAfter.model.x-pointCurrent.model.x)/3;
				pointCurrent.model.controlPointNextX=pointCurrent.model.x+deltaX;
				pointCurrent.model.controlPointNextY=pointCurrent.model.y+deltaX*pointCurrent.mK;
			}
		}
	};
	helpers$1.nextItem=function(collection,index,loop){
		if(loop){
			returnindex>=collection.length-1?collection[0]:collection[index+1];
		}
		returnindex>=collection.length-1?collection[collection.length-1]:collection[index+1];
	};
	helpers$1.previousItem=function(collection,index,loop){
		if(loop){
			returnindex<=0?collection[collection.length-1]:collection[index-1];
		}
		returnindex<=0?collection[0]:collection[index-1];
	};
	//Implementationofthenicenumberalgorithmusedindeterminingwhereaxislabelswillgo
	helpers$1.niceNum=function(range,round){
		varexponent=Math.floor(helpers$1.log10(range));
		varfraction=range/Math.pow(10,exponent);
		varniceFraction;

		if(round){
			if(fraction<1.5){
				niceFraction=1;
			}elseif(fraction<3){
				niceFraction=2;
			}elseif(fraction<7){
				niceFraction=5;
			}else{
				niceFraction=10;
			}
		}elseif(fraction<=1.0){
			niceFraction=1;
		}elseif(fraction<=2){
			niceFraction=2;
		}elseif(fraction<=5){
			niceFraction=5;
		}else{
			niceFraction=10;
		}

		returnniceFraction*Math.pow(10,exponent);
	};
	//Requestanimationpolyfill-https://www.paulirish.com/2011/requestanimationframe-for-smart-animating/
	helpers$1.requestAnimFrame=(function(){
		if(typeofwindow==='undefined'){
			returnfunction(callback){
				callback();
			};
		}
		returnwindow.requestAnimationFrame||
			window.webkitRequestAnimationFrame||
			window.mozRequestAnimationFrame||
			window.oRequestAnimationFrame||
			window.msRequestAnimationFrame||
			function(callback){
				returnwindow.setTimeout(callback,1000/60);
			};
	}());
	//--DOMmethods
	helpers$1.getRelativePosition=function(evt,chart){
		varmouseX,mouseY;
		vare=evt.originalEvent||evt;
		varcanvas=evt.target||evt.srcElement;
		varboundingRect=canvas.getBoundingClientRect();

		vartouches=e.touches;
		if(touches&&touches.length>0){
			mouseX=touches[0].clientX;
			mouseY=touches[0].clientY;

		}else{
			mouseX=e.clientX;
			mouseY=e.clientY;
		}

		//Scalemousecoordinatesintocanvascoordinates
		//byfollowingthepatternlaidoutby'jerryj'inthecommentsof
		//https://www.html5canvastutorials.com/advanced/html5-canvas-mouse-coordinates/
		varpaddingLeft=parseFloat(helpers$1.getStyle(canvas,'padding-left'));
		varpaddingTop=parseFloat(helpers$1.getStyle(canvas,'padding-top'));
		varpaddingRight=parseFloat(helpers$1.getStyle(canvas,'padding-right'));
		varpaddingBottom=parseFloat(helpers$1.getStyle(canvas,'padding-bottom'));
		varwidth=boundingRect.right-boundingRect.left-paddingLeft-paddingRight;
		varheight=boundingRect.bottom-boundingRect.top-paddingTop-paddingBottom;

		//Wedividebythecurrentdevicepixelratio,becausethecanvasisscaledupbythatamountineachdirection.However
		//thebackendmodelisinunscaledcoordinates.Sincewearegoingtodealwithourmodelcoordinates,wegobackhere
		mouseX=Math.round((mouseX-boundingRect.left-paddingLeft)/(width)*canvas.width/chart.currentDevicePixelRatio);
		mouseY=Math.round((mouseY-boundingRect.top-paddingTop)/(height)*canvas.height/chart.currentDevicePixelRatio);

		return{
			x:mouseX,
			y:mouseY
		};

	};

	//Privatehelperfunctiontoconvertmax-width/max-heightvaluesthatmaybepercentagesintoanumber
	functionparseMaxStyle(styleValue,node,parentProperty){
		varvalueInPixels;
		if(typeofstyleValue==='string'){
			valueInPixels=parseInt(styleValue,10);

			if(styleValue.indexOf('%')!==-1){
				//percentage*sizeindimension
				valueInPixels=valueInPixels/100*node.parentNode[parentProperty];
			}
		}else{
			valueInPixels=styleValue;
		}

		returnvalueInPixels;
	}

	/**
	*Returnsifthegivenvaluecontainsaneffectiveconstraint.
	*@private
	*/
	functionisConstrainedValue(value){
		returnvalue!==undefined&&value!==null&&value!=='none';
	}

	/**
	*ReturnsthemaxwidthorheightofthegivenDOMnodeinacross-browsercompatiblefashion
	*@param{HTMLElement}domNode-thenodetochecktheconstrainton
	*@param{string}maxStyle-thestylethatdefinesthemaximumforthedirectionweareusing('max-width'/'max-height')
	*@param{string}percentageProperty-propertyofparenttousewhencalculatingwidthasapercentage
	*@see{@linkhttps://www.nathanaeljones.com/blog/2013/reading-max-width-cross-browser}
	*/
	functiongetConstraintDimension(domNode,maxStyle,percentageProperty){
		varview=document.defaultView;
		varparentNode=helpers$1._getParentNode(domNode);
		varconstrainedNode=view.getComputedStyle(domNode)[maxStyle];
		varconstrainedContainer=view.getComputedStyle(parentNode)[maxStyle];
		varhasCNode=isConstrainedValue(constrainedNode);
		varhasCContainer=isConstrainedValue(constrainedContainer);
		varinfinity=Number.POSITIVE_INFINITY;

		if(hasCNode||hasCContainer){
			returnMath.min(
				hasCNode?parseMaxStyle(constrainedNode,domNode,percentageProperty):infinity,
				hasCContainer?parseMaxStyle(constrainedContainer,parentNode,percentageProperty):infinity);
		}

		return'none';
	}
	//returnsNumberorundefinedifnoconstraint
	helpers$1.getConstraintWidth=function(domNode){
		returngetConstraintDimension(domNode,'max-width','clientWidth');
	};
	//returnsNumberorundefinedifnoconstraint
	helpers$1.getConstraintHeight=function(domNode){
		returngetConstraintDimension(domNode,'max-height','clientHeight');
	};
	/**
	*@private
 	*/
	helpers$1._calculatePadding=function(container,padding,parentDimension){
		padding=helpers$1.getStyle(container,padding);

		returnpadding.indexOf('%')>-1?parentDimension*parseInt(padding,10)/100:parseInt(padding,10);
	};
	/**
	*@private
	*/
	helpers$1._getParentNode=function(domNode){
		varparent=domNode.parentNode;
		if(parent&&parent.toString()==='[objectShadowRoot]'){
			parent=parent.host;
		}
		returnparent;
	};
	helpers$1.getMaximumWidth=function(domNode){
		varcontainer=helpers$1._getParentNode(domNode);
		if(!container){
			returndomNode.getBoundingClientRect().width; //Flectracustomization
		}

		varclientWidth=container.getBoundingClientRect().width; //Flectracustomization
		varpaddingLeft=helpers$1._calculatePadding(container,'padding-left',clientWidth);
		varpaddingRight=helpers$1._calculatePadding(container,'padding-right',clientWidth);

		varw=clientWidth-paddingLeft-paddingRight;
		varcw=helpers$1.getConstraintWidth(domNode);
		returnisNaN(cw)?w:Math.min(w,cw);
	};
	helpers$1.getMaximumHeight=function(domNode){
		varcontainer=helpers$1._getParentNode(domNode);
		if(!container){
			returndomNode.getBoundingClientRect().height; //Flectracustomization
		}

		varclientHeight=container.getBoundingClientRect().height; //Flectracustomization
		varpaddingTop=helpers$1._calculatePadding(container,'padding-top',clientHeight);
		varpaddingBottom=helpers$1._calculatePadding(container,'padding-bottom',clientHeight);

		varh=clientHeight-paddingTop-paddingBottom;
		varch=helpers$1.getConstraintHeight(domNode);
		returnisNaN(ch)?h:Math.min(h,ch);
	};
	helpers$1.getStyle=function(el,property){
		returnel.currentStyle?
			el.currentStyle[property]:
			document.defaultView.getComputedStyle(el,null).getPropertyValue(property);
	};
	helpers$1.retinaScale=function(chart,forceRatio){
		varpixelRatio=chart.currentDevicePixelRatio=forceRatio||(typeofwindow!=='undefined'&&window.devicePixelRatio)||1;
		if(pixelRatio===1){
			return;
		}

		varcanvas=chart.canvas;
		varheight=chart.height;
		varwidth=chart.width;

		canvas.height=height*pixelRatio;
		canvas.width=width*pixelRatio;
		chart.ctx.scale(pixelRatio,pixelRatio);

		//Ifnostylehasbeensetonthecanvas,therendersizeisusedasdisplaysize,
		//makingthechartvisuallybigger,solet'senforceittothe"correct"values.
		//Seehttps://github.com/chartjs/Chart.js/issues/3575
		if(!canvas.style.height&&!canvas.style.width){
			canvas.style.height=height+'px';
			canvas.style.width=width+'px';
		}
	};
	//--Canvasmethods
	helpers$1.fontString=function(pixelSize,fontStyle,fontFamily){
		returnfontStyle+''+pixelSize+'px'+fontFamily;
	};
	helpers$1.longestText=function(ctx,font,arrayOfThings,cache){
		cache=cache||{};
		vardata=cache.data=cache.data||{};
		vargc=cache.garbageCollect=cache.garbageCollect||[];

		if(cache.font!==font){
			data=cache.data={};
			gc=cache.garbageCollect=[];
			cache.font=font;
		}

		ctx.font=font;
		varlongest=0;
		varilen=arrayOfThings.length;
		vari,j,jlen,thing,nestedThing;
		for(i=0;i<ilen;i++){
			thing=arrayOfThings[i];

			//Undefinedstringsandarraysshouldnotbemeasured
			if(thing!==undefined&&thing!==null&&helpers$1.isArray(thing)!==true){
				longest=helpers$1.measureText(ctx,data,gc,longest,thing);
			}elseif(helpers$1.isArray(thing)){
				//ifitisanarrayletsmeasureeachelement
				//todomaybesimplifythisfunctionabitsowecandothismorerecursively?
				for(j=0,jlen=thing.length;j<jlen;j++){
					nestedThing=thing[j];
					//Undefinedstringsandarraysshouldnotbemeasured
					if(nestedThing!==undefined&&nestedThing!==null&&!helpers$1.isArray(nestedThing)){
						longest=helpers$1.measureText(ctx,data,gc,longest,nestedThing);
					}
				}
			}
		}

		vargcLen=gc.length/2;
		if(gcLen>arrayOfThings.length){
			for(i=0;i<gcLen;i++){
				deletedata[gc[i]];
			}
			gc.splice(0,gcLen);
		}
		returnlongest;
	};
	helpers$1.measureText=function(ctx,data,gc,longest,string){
		vartextWidth=data[string];
		if(!textWidth){
			textWidth=data[string]=ctx.measureText(string).width;
			gc.push(string);
		}
		if(textWidth>longest){
			longest=textWidth;
		}
		returnlongest;
	};

	/**
	*@deprecated
	*/
	helpers$1.numberOfLabelLines=function(arrayOfThings){
		varnumberOfLines=1;
		helpers$1.each(arrayOfThings,function(thing){
			if(helpers$1.isArray(thing)){
				if(thing.length>numberOfLines){
					numberOfLines=thing.length;
				}
			}
		});
		returnnumberOfLines;
	};

	helpers$1.color=!chartjsColor?
		function(value){
			console.error('Color.jsnotfound!');
			returnvalue;
		}:
		function(value){
			/*globalCanvasGradient*/
			if(valueinstanceofCanvasGradient){
				value=core_defaults.global.defaultColor;
			}

			returnchartjsColor(value);
		};

	helpers$1.getHoverColor=function(colorValue){
		/*globalCanvasPattern*/
		return(colorValueinstanceofCanvasPattern||colorValueinstanceofCanvasGradient)?
			colorValue:
			helpers$1.color(colorValue).saturate(0.5).darken(0.1).rgbString();
	};
};

functionabstract(){
	thrownewError(
		'Thismethodisnotimplemented:eithernoadaptercan'+
		'befoundoranincompleteintegrationwasprovided.'
	);
}

/**
 *Dateadapter(currentusedbythetimescale)
 *@namespaceChart._adapters._date
 *@memberofChart._adapters
 *@private
 */

/**
 *Currentlysupportedunitstringvalues.
 *@typedef{('millisecond'|'second'|'minute'|'hour'|'day'|'week'|'month'|'quarter'|'year')}
 *@memberofChart._adapters._date
 *@nameUnit
 */

/**
 *@class
 */
functionDateAdapter(options){
	this.options=options||{};
}

helpers$1.extend(DateAdapter.prototype,/**@lendsDateAdapter*/{
	/**
	*Returnsamapoftimeformatsforthesupportedformattingunitsdefined
	*inUnitaswellas'datetime'representingadetaileddate/timestring.
	*@returns{{string:string}}
	*/
	formats:abstract,

	/**
	*Parsesthegiven`value`andreturntheassociatedtimestamp.
	*@param{any}value-thevaluetoparse(usuallycomesfromthedata)
	*@param{string}[format]-theexpecteddataformat
	*@returns{(number|null)}
	*@function
	*/
	parse:abstract,

	/**
	*Returnstheformatteddateinthespecified`format`foragiven`timestamp`.
	*@param{number}timestamp-thetimestamptoformat
	*@param{string}format-thedate/timetoken
	*@return{string}
	*@function
	*/
	format:abstract,

	/**
	*Addsthespecified`amount`of`unit`tothegiven`timestamp`.
	*@param{number}timestamp-theinputtimestamp
	*@param{number}amount-theamounttoadd
	*@param{Unit}unit-theunitasstring
	*@return{number}
	*@function
	*/
	add:abstract,

	/**
	*Returnsthenumberof`unit`betweenthegiventimestamps.
	*@param{number}max-theinputtimestamp(reference)
	*@param{number}min-thetimestamptosubstract
	*@param{Unit}unit-theunitasstring
	*@return{number}
	*@function
	*/
	diff:abstract,

	/**
	*Returnsstartof`unit`forthegiven`timestamp`.
	*@param{number}timestamp-theinputtimestamp
	*@param{Unit}unit-theunitasstring
	*@param{number}[weekday]-theISOdayoftheweekwith1beingMonday
	*and7beingSunday(onlyneededifparam*unit*is`isoWeek`).
	*@function
	*/
	startOf:abstract,

	/**
	*Returnsendof`unit`forthegiven`timestamp`.
	*@param{number}timestamp-theinputtimestamp
	*@param{Unit}unit-theunitasstring
	*@function
	*/
	endOf:abstract,

	//DEPRECATIONS

	/**
	*Providedforbackwardcompatibilityforscale.getValueForPixel(),
	*thismethodshouldbeoverriddenonlybythemomentadapter.
	*@deprecatedsinceversion2.8.0
	*@todoremoveatversion3
	*@private
	*/
	_create:function(value){
		returnvalue;
	}
});

DateAdapter.override=function(members){
	helpers$1.extend(DateAdapter.prototype,members);
};

var_date=DateAdapter;

varcore_adapters={
	_date:_date
};

/**
 *Namespacetoholdstatictickgenerationfunctions
 *@namespaceChart.Ticks
 */
varcore_ticks={
	/**
	*Namespacetoholdformattersfordifferenttypesofticks
	*@namespaceChart.Ticks.formatters
	*/
	formatters:{
		/**
		*Formatterforvaluelabels
		*@methodChart.Ticks.formatters.values
		*@paramvaluethevaluetodisplay
		*@return{string|string[]}thelabeltodisplay
		*/
		values:function(value){
			returnhelpers$1.isArray(value)?value:''+value;
		},

		/**
		*Formatterforlinearnumericticks
		*@methodChart.Ticks.formatters.linear
		*@paramtickValue{number}thevaluetobeformatted
		*@paramindex{number}thepositionofthetickValueparameterintheticksarray
		*@paramticks{number[]}thelistofticksbeingconverted
		*@return{string}stringrepresentationofthetickValueparameter
		*/
		linear:function(tickValue,index,ticks){
			//Ifwehavelotsofticks,don'tusetheones
			vardelta=ticks.length>3?ticks[2]-ticks[1]:ticks[1]-ticks[0];

			//Ifwehaveanumberlike2.5asthedelta,figureouthowmanydecimalplacesweneed
			if(Math.abs(delta)>1){
				if(tickValue!==Math.floor(tickValue)){
					//notaninteger
					delta=tickValue-Math.floor(tickValue);
				}
			}

			varlogDelta=helpers$1.log10(Math.abs(delta));
			vartickString='';

			if(tickValue!==0){
				varmaxTick=Math.max(Math.abs(ticks[0]),Math.abs(ticks[ticks.length-1]));
				if(maxTick<1e-4){//allticksaresmallnumbers;usescientificnotation
					varlogTick=helpers$1.log10(Math.abs(tickValue));
					varnumExponential=Math.floor(logTick)-Math.floor(logDelta);
					numExponential=Math.max(Math.min(numExponential,20),0);
					tickString=tickValue.toExponential(numExponential);
				}else{
					varnumDecimal=-1*Math.floor(logDelta);
					numDecimal=Math.max(Math.min(numDecimal,20),0);//toFixedhasamaxof20decimalplaces
					tickString=tickValue.toFixed(numDecimal);
				}
			}else{
				tickString='0';//nevershowdecimalplacesfor0
			}

			returntickString;
		},

		logarithmic:function(tickValue,index,ticks){
			varremain=tickValue/(Math.pow(10,Math.floor(helpers$1.log10(tickValue))));

			if(tickValue===0){
				return'0';
			}elseif(remain===1||remain===2||remain===5||index===0||index===ticks.length-1){
				returntickValue.toExponential();
			}
			return'';
		}
	}
};

varisArray=helpers$1.isArray;
varisNullOrUndef=helpers$1.isNullOrUndef;
varvalueOrDefault$a=helpers$1.valueOrDefault;
varvalueAtIndexOrDefault=helpers$1.valueAtIndexOrDefault;

core_defaults._set('scale',{
	display:true,
	position:'left',
	offset:false,

	//gridlinesettings
	gridLines:{
		display:true,
		color:'rgba(0,0,0,0.1)',
		lineWidth:1,
		drawBorder:true,
		drawOnChartArea:true,
		drawTicks:true,
		tickMarkLength:10,
		zeroLineWidth:1,
		zeroLineColor:'rgba(0,0,0,0.25)',
		zeroLineBorderDash:[],
		zeroLineBorderDashOffset:0.0,
		offsetGridLines:false,
		borderDash:[],
		borderDashOffset:0.0
	},

	//scalelabel
	scaleLabel:{
		//displayproperty
		display:false,

		//actuallabel
		labelString:'',

		//top/bottompadding
		padding:{
			top:4,
			bottom:4
		}
	},

	//labelsettings
	ticks:{
		beginAtZero:false,
		minRotation:0,
		maxRotation:50,
		mirror:false,
		padding:0,
		reverse:false,
		display:true,
		autoSkip:true,
		autoSkipPadding:0,
		labelOffset:0,
		//Wepassthrougharraystoberenderedasmultilinelabels,weconvertOtherstostringshere.
		callback:core_ticks.formatters.values,
		minor:{},
		major:{}
	}
});

/**ReturnsanewarraycontainingnumItemsfromarr*/
functionsample(arr,numItems){
	varresult=[];
	varincrement=arr.length/numItems;
	vari=0;
	varlen=arr.length;

	for(;i<len;i+=increment){
		result.push(arr[Math.floor(i)]);
	}
	returnresult;
}

functiongetPixelForGridLine(scale,index,offsetGridLines){
	varlength=scale.getTicks().length;
	varvalidIndex=Math.min(index,length-1);
	varlineValue=scale.getPixelForTick(validIndex);
	varstart=scale._startPixel;
	varend=scale._endPixel;
	varepsilon=1e-6;//1e-6ismargininpixelsforaccumulatederror.
	varoffset;

	if(offsetGridLines){
		if(length===1){
			offset=Math.max(lineValue-start,end-lineValue);
		}elseif(index===0){
			offset=(scale.getPixelForTick(1)-lineValue)/2;
		}else{
			offset=(lineValue-scale.getPixelForTick(validIndex-1))/2;
		}
		lineValue+=validIndex<index?offset:-offset;

		//Returnundefinedifthepixelisoutoftherange
		if(lineValue<start-epsilon||lineValue>end+epsilon){
			return;
		}
	}
	returnlineValue;
}

functiongarbageCollect(caches,length){
	helpers$1.each(caches,function(cache){
		vargc=cache.gc;
		vargcLen=gc.length/2;
		vari;
		if(gcLen>length){
			for(i=0;i<gcLen;++i){
				deletecache.data[gc[i]];
			}
			gc.splice(0,gcLen);
		}
	});
}

/**
 *Returns{width,height,offset}objectsforthefirst,last,widest,highesttick
 *labelswhereoffsetindicatestheanchorpointoffsetfromthetopinpixels.
 */
functioncomputeLabelSizes(ctx,tickFonts,ticks,caches){
	varlength=ticks.length;
	varwidths=[];
	varheights=[];
	varoffsets=[];
	varwidestLabelSize=0;
	varhighestLabelSize=0;
	vari,j,jlen,label,tickFont,fontString,cache,lineHeight,width,height,nestedLabel,widest,highest;

	for(i=0;i<length;++i){
		label=ticks[i].label;
		tickFont=ticks[i].major?tickFonts.major:tickFonts.minor;
		ctx.font=fontString=tickFont.string;
		cache=caches[fontString]=caches[fontString]||{data:{},gc:[]};
		lineHeight=tickFont.lineHeight;
		width=height=0;
		//Undefinedlabelsandarraysshouldnotbemeasured
		if(!isNullOrUndef(label)&&!isArray(label)){
			width=helpers$1.measureText(ctx,cache.data,cache.gc,width,label);
			height=lineHeight;
		}elseif(isArray(label)){
			//ifitisanarraylet'smeasureeachelement
			for(j=0,jlen=label.length;j<jlen;++j){
				nestedLabel=label[j];
				//Undefinedlabelsandarraysshouldnotbemeasured
				if(!isNullOrUndef(nestedLabel)&&!isArray(nestedLabel)){
					width=helpers$1.measureText(ctx,cache.data,cache.gc,width,nestedLabel);
					height+=lineHeight;
				}
			}
		}
		widths.push(width);
		heights.push(height);
		offsets.push(lineHeight/2);
		widestLabelSize=Math.max(width,widestLabelSize);
		highestLabelSize=Math.max(height,highestLabelSize);
	}
	garbageCollect(caches,length);

	widest=widths.indexOf(widestLabelSize);
	highest=heights.indexOf(highestLabelSize);

	functionvalueAt(idx){
		return{
			width:widths[idx]||0,
			height:heights[idx]||0,
			offset:offsets[idx]||0
		};
	}

	return{
		first:valueAt(0),
		last:valueAt(length-1),
		widest:valueAt(widest),
		highest:valueAt(highest)
	};
}

functiongetTickMarkLength(options){
	returnoptions.drawTicks?options.tickMarkLength:0;
}

functiongetScaleLabelHeight(options){
	varfont,padding;

	if(!options.display){
		return0;
	}

	font=helpers$1.options._parseFont(options);
	padding=helpers$1.options.toPadding(options.padding);

	returnfont.lineHeight+padding.height;
}

functionparseFontOptions(options,nestedOpts){
	returnhelpers$1.extend(helpers$1.options._parseFont({
		fontFamily:valueOrDefault$a(nestedOpts.fontFamily,options.fontFamily),
		fontSize:valueOrDefault$a(nestedOpts.fontSize,options.fontSize),
		fontStyle:valueOrDefault$a(nestedOpts.fontStyle,options.fontStyle),
		lineHeight:valueOrDefault$a(nestedOpts.lineHeight,options.lineHeight)
	}),{
		color:helpers$1.options.resolve([nestedOpts.fontColor,options.fontColor,core_defaults.global.defaultFontColor])
	});
}

functionparseTickFontOptions(options){
	varminor=parseFontOptions(options,options.minor);
	varmajor=options.major.enabled?parseFontOptions(options,options.major):minor;

	return{minor:minor,major:major};
}

functionnonSkipped(ticksToFilter){
	varfiltered=[];
	varitem,index,len;
	for(index=0,len=ticksToFilter.length;index<len;++index){
		item=ticksToFilter[index];
		if(typeofitem._index!=='undefined'){
			filtered.push(item);
		}
	}
	returnfiltered;
}

functiongetEvenSpacing(arr){
	varlen=arr.length;
	vari,diff;

	if(len<2){
		returnfalse;
	}

	for(diff=arr[0],i=1;i<len;++i){
		if(arr[i]-arr[i-1]!==diff){
			returnfalse;
		}
	}
	returndiff;
}

functioncalculateSpacing(majorIndices,ticks,axisLength,ticksLimit){
	varevenMajorSpacing=getEvenSpacing(majorIndices);
	varspacing=(ticks.length-1)/ticksLimit;
	varfactors,factor,i,ilen;

	//Ifthemajorticksareevenlyspacedapart,placetheminorticks
	//sothattheydividethemajorticksintoevenchunks
	if(!evenMajorSpacing){
		returnMath.max(spacing,1);
	}

	factors=helpers$1.math._factorize(evenMajorSpacing);
	for(i=0,ilen=factors.length-1;i<ilen;i++){
		factor=factors[i];
		if(factor>spacing){
			returnfactor;
		}
	}
	returnMath.max(spacing,1);
}

functiongetMajorIndices(ticks){
	varresult=[];
	vari,ilen;
	for(i=0,ilen=ticks.length;i<ilen;i++){
		if(ticks[i].major){
			result.push(i);
		}
	}
	returnresult;
}

functionskipMajors(ticks,majorIndices,spacing){
	varcount=0;
	varnext=majorIndices[0];
	vari,tick;

	spacing=Math.ceil(spacing);
	for(i=0;i<ticks.length;i++){
		tick=ticks[i];
		if(i===next){
			tick._index=i;
			count++;
			next=majorIndices[count*spacing];
		}else{
			deletetick.label;
		}
	}
}

functionskip(ticks,spacing,majorStart,majorEnd){
	varstart=valueOrDefault$a(majorStart,0);
	varend=Math.min(valueOrDefault$a(majorEnd,ticks.length),ticks.length);
	varcount=0;
	varlength,i,tick,next;

	spacing=Math.ceil(spacing);
	if(majorEnd){
		length=majorEnd-majorStart;
		spacing=length/Math.floor(length/spacing);
	}

	next=start;

	while(next<0){
		count++;
		next=Math.round(start+count*spacing);
	}

	for(i=Math.max(start,0);i<end;i++){
		tick=ticks[i];
		if(i===next){
			tick._index=i;
			count++;
			next=Math.round(start+count*spacing);
		}else{
			deletetick.label;
		}
	}
}

varScale=core_element.extend({

	zeroLineIndex:0,

	/**
	*Getthepaddingneededforthescale
	*@methodgetPadding
	*@private
	*@returns{Padding}thenecessarypadding
	*/
	getPadding:function(){
		varme=this;
		return{
			left:me.paddingLeft||0,
			top:me.paddingTop||0,
			right:me.paddingRight||0,
			bottom:me.paddingBottom||0
		};
	},

	/**
	*Returnsthescaletickobjects({label,major})
	*@since2.7
	*/
	getTicks:function(){
		returnthis._ticks;
	},

	/**
	*@private
	*/
	_getLabels:function(){
		vardata=this.chart.data;
		returnthis.options.labels||(this.isHorizontal()?data.xLabels:data.yLabels)||data.labels||[];
	},

	//Thesemethodsareorderedbylifecyle.Utilitiesthenfollow.
	//Anyfunctiondefinedhereisinheritedbyallscaletypes.
	//Anyfunctioncanbeextendedbythescaletype

	/**
	*Providedforbackwardcompatibility,notavailableanymore
	*@functionChart.Scale.mergeTicksOptions
	*@deprecatedsinceversion2.8.0
	*@todoremoveatversion3
	*/
	mergeTicksOptions:function(){
		//noop
	},

	beforeUpdate:function(){
		helpers$1.callback(this.options.beforeUpdate,[this]);
	},

	/**
	*@param{number}maxWidth-themaxwidthinpixels
	*@param{number}maxHeight-themaxheightinpixels
	*@param{object}margins-thespacebetweentheedgeoftheotherscalesandedgeofthechart
	*  Thisspacecomesfromtwosources:
	*    -padding-spacethat'srequiredtoshowthelabelsattheedgesofthescale
	*    -thicknessofscalesorlegendsinanotherorientation
	*/
	update:function(maxWidth,maxHeight,margins){
		varme=this;
		vartickOpts=me.options.ticks;
		varsampleSize=tickOpts.sampleSize;
		vari,ilen,labels,ticks,samplingEnabled;

		//UpdateLifecycle-Probablydon'twanttoeverextendoroverwritethisfunction;)
		me.beforeUpdate();

		//Absorbthemastermeasurements
		me.maxWidth=maxWidth;
		me.maxHeight=maxHeight;
		me.margins=helpers$1.extend({
			left:0,
			right:0,
			top:0,
			bottom:0
		},margins);

		me._ticks=null;
		me.ticks=null;
		me._labelSizes=null;
		me._maxLabelLines=0;
		me.longestLabelWidth=0;
		me.longestTextCache=me.longestTextCache||{};
		me._gridLineItems=null;
		me._labelItems=null;

		//Dimensions
		me.beforeSetDimensions();
		me.setDimensions();
		me.afterSetDimensions();

		//Datamin/max
		me.beforeDataLimits();
		me.determineDataLimits();
		me.afterDataLimits();

		//Ticks-`this.ticks`isnowDEPRECATED!
		//InternalticksarenowstoredasobjectsinthePRIVATE`this._ticks`member
		//andmustnotbeaccesseddirectlyfromoutsidethisclass.`this.ticks`being
		//aroundforlongtimeandnotmarkedasprivate,wecan'tchangeitsstructure
		//withoutunexpectedbreakingchanges.Ifyouneedtoaccessthescaleticks,
		//usescale.getTicks()instead.

		me.beforeBuildTicks();

		//NewimplementationsshouldreturnanarrayofobjectsbutforBACKWARDCOMPAT,
		//westillsupportnoreturn(`this.ticks`internallysetbycallingthismethod).
		ticks=me.buildTicks()||[];

		//Allowmodificationofticksincallback.
		ticks=me.afterBuildTicks(ticks)||ticks;

		//Ensuretickscontainsticksinnewtickformat
		if((!ticks||!ticks.length)&&me.ticks){
			ticks=[];
			for(i=0,ilen=me.ticks.length;i<ilen;++i){
				ticks.push({
					value:me.ticks[i],
					major:false
				});
			}
		}

		me._ticks=ticks;

		//Computetickrotationandfitusingasampledsubsetoflabels
		//Wegenerallydon'tneedtocomputethesizeofeverysinglelabelfordeterminingscalesize
		samplingEnabled=sampleSize<ticks.length;
		labels=me._convertTicksToLabels(samplingEnabled?sample(ticks,sampleSize):ticks);

		//_configureiscalledtwice,oncehere,oncefromcore.controller.updateLayout.
		//Herewehaven'tbeenpositionedyet,butdimensionsarecorrect.
		//Variablessetin_configureareneededforcalculateTickRotation,and
		//it'sokthatcoordinatesarenotcorrectthere,onlydimensionsmatter.
		me._configure();

		//TickRotation
		me.beforeCalculateTickRotation();
		me.calculateTickRotation();
		me.afterCalculateTickRotation();

		me.beforeFit();
		me.fit();
		me.afterFit();

		//Auto-skip
		me._ticksToDraw=tickOpts.display&&(tickOpts.autoSkip||tickOpts.source==='auto')?me._autoSkip(ticks):ticks;

		if(samplingEnabled){
			//Generatelabelsusingallnon-skippedticks
			labels=me._convertTicksToLabels(me._ticksToDraw);
		}

		me.ticks=labels;  //BACKWARDCOMPATIBILITY

		//IMPORTANT:afterthispoint,weconsiderthat`this.ticks`willNEVERchange!

		me.afterUpdate();

		//TODO(v3):removeminSizeasapublicpropertyandreturnvaluefromalllayoutboxes.Itisunused
		//makemaxWidthandmaxHeightprivate
		returnme.minSize;
	},

	/**
	*@private
	*/
	_configure:function(){
		varme=this;
		varreversePixels=me.options.ticks.reverse;
		varstartPixel,endPixel;

		if(me.isHorizontal()){
			startPixel=me.left;
			endPixel=me.right;
		}else{
			startPixel=me.top;
			endPixel=me.bottom;
			//bydefaultverticalscalesarefrombottomtotop,sopixelsarereversed
			reversePixels=!reversePixels;
		}
		me._startPixel=startPixel;
		me._endPixel=endPixel;
		me._reversePixels=reversePixels;
		me._length=endPixel-startPixel;
	},

	afterUpdate:function(){
		helpers$1.callback(this.options.afterUpdate,[this]);
	},

	//

	beforeSetDimensions:function(){
		helpers$1.callback(this.options.beforeSetDimensions,[this]);
	},
	setDimensions:function(){
		varme=this;
		//Settheunconstraineddimensionbeforelabelrotation
		if(me.isHorizontal()){
			//Resetpositionbeforecalculatingrotation
			me.width=me.maxWidth;
			me.left=0;
			me.right=me.width;
		}else{
			me.height=me.maxHeight;

			//Resetpositionbeforecalculatingrotation
			me.top=0;
			me.bottom=me.height;
		}

		//Resetpadding
		me.paddingLeft=0;
		me.paddingTop=0;
		me.paddingRight=0;
		me.paddingBottom=0;
	},
	afterSetDimensions:function(){
		helpers$1.callback(this.options.afterSetDimensions,[this]);
	},

	//Datalimits
	beforeDataLimits:function(){
		helpers$1.callback(this.options.beforeDataLimits,[this]);
	},
	determineDataLimits:helpers$1.noop,
	afterDataLimits:function(){
		helpers$1.callback(this.options.afterDataLimits,[this]);
	},

	//
	beforeBuildTicks:function(){
		helpers$1.callback(this.options.beforeBuildTicks,[this]);
	},
	buildTicks:helpers$1.noop,
	afterBuildTicks:function(ticks){
		varme=this;
		//ticksisemptyforoldaxisimplementationshere
		if(isArray(ticks)&&ticks.length){
			returnhelpers$1.callback(me.options.afterBuildTicks,[me,ticks]);
		}
		//Supportoldimplementations(thatmodified`this.ticks`directlyinbuildTicks)
		me.ticks=helpers$1.callback(me.options.afterBuildTicks,[me,me.ticks])||me.ticks;
		returnticks;
	},

	beforeTickToLabelConversion:function(){
		helpers$1.callback(this.options.beforeTickToLabelConversion,[this]);
	},
	convertTicksToLabels:function(){
		varme=this;
		//Converttickstostrings
		vartickOpts=me.options.ticks;
		me.ticks=me.ticks.map(tickOpts.userCallback||tickOpts.callback,this);
	},
	afterTickToLabelConversion:function(){
		helpers$1.callback(this.options.afterTickToLabelConversion,[this]);
	},

	//

	beforeCalculateTickRotation:function(){
		helpers$1.callback(this.options.beforeCalculateTickRotation,[this]);
	},
	calculateTickRotation:function(){
		varme=this;
		varoptions=me.options;
		vartickOpts=options.ticks;
		varnumTicks=me.getTicks().length;
		varminRotation=tickOpts.minRotation||0;
		varmaxRotation=tickOpts.maxRotation;
		varlabelRotation=minRotation;
		varlabelSizes,maxLabelWidth,maxLabelHeight,maxWidth,tickWidth,maxHeight,maxLabelDiagonal;

		if(!me._isVisible()||!tickOpts.display||minRotation>=maxRotation||numTicks<=1||!me.isHorizontal()){
			me.labelRotation=minRotation;
			return;
		}

		labelSizes=me._getLabelSizes();
		maxLabelWidth=labelSizes.widest.width;
		maxLabelHeight=labelSizes.highest.height-labelSizes.highest.offset;

		//Estimatethewidthofeachgridbasedonthecanvaswidth,themaximum
		//labelwidthandthenumberoftickintervals
		maxWidth=Math.min(me.maxWidth,me.chart.width-maxLabelWidth);
		tickWidth=options.offset?me.maxWidth/numTicks:maxWidth/(numTicks-1);

		//Allow3pixelsx2paddingeithersideforlabelreadability
		if(maxLabelWidth+6>tickWidth){
			tickWidth=maxWidth/(numTicks-(options.offset?0.5:1));
			maxHeight=me.maxHeight-getTickMarkLength(options.gridLines)
				-tickOpts.padding-getScaleLabelHeight(options.scaleLabel);
			maxLabelDiagonal=Math.sqrt(maxLabelWidth*maxLabelWidth+maxLabelHeight*maxLabelHeight);
			labelRotation=helpers$1.toDegrees(Math.min(
				Math.asin(Math.min((labelSizes.highest.height+6)/tickWidth,1)),
				Math.asin(Math.min(maxHeight/maxLabelDiagonal,1))-Math.asin(maxLabelHeight/maxLabelDiagonal)
			));
			labelRotation=Math.max(minRotation,Math.min(maxRotation,labelRotation));
		}

		me.labelRotation=labelRotation;
	},
	afterCalculateTickRotation:function(){
		helpers$1.callback(this.options.afterCalculateTickRotation,[this]);
	},

	//

	beforeFit:function(){
		helpers$1.callback(this.options.beforeFit,[this]);
	},
	fit:function(){
		varme=this;
		//Reset
		varminSize=me.minSize={
			width:0,
			height:0
		};

		varchart=me.chart;
		varopts=me.options;
		vartickOpts=opts.ticks;
		varscaleLabelOpts=opts.scaleLabel;
		vargridLineOpts=opts.gridLines;
		vardisplay=me._isVisible();
		varisBottom=opts.position==='bottom';
		varisHorizontal=me.isHorizontal();

		//Width
		if(isHorizontal){
			minSize.width=me.maxWidth;
		}elseif(display){
			minSize.width=getTickMarkLength(gridLineOpts)+getScaleLabelHeight(scaleLabelOpts);
		}

		//height
		if(!isHorizontal){
			minSize.height=me.maxHeight;//fillalltheheight
		}elseif(display){
			minSize.height=getTickMarkLength(gridLineOpts)+getScaleLabelHeight(scaleLabelOpts);
		}

		//Don'tbotherfittingtheticksifwearenotshowingthelabels
		if(tickOpts.display&&display){
			vartickFonts=parseTickFontOptions(tickOpts);
			varlabelSizes=me._getLabelSizes();
			varfirstLabelSize=labelSizes.first;
			varlastLabelSize=labelSizes.last;
			varwidestLabelSize=labelSizes.widest;
			varhighestLabelSize=labelSizes.highest;
			varlineSpace=tickFonts.minor.lineHeight*0.4;
			vartickPadding=tickOpts.padding;

			if(isHorizontal){
				//Ahorizontalaxisismoreconstrainedbytheheight.
				varisRotated=me.labelRotation!==0;
				varangleRadians=helpers$1.toRadians(me.labelRotation);
				varcosRotation=Math.cos(angleRadians);
				varsinRotation=Math.sin(angleRadians);

				varlabelHeight=sinRotation*widestLabelSize.width
					+cosRotation*(highestLabelSize.height-(isRotated?highestLabelSize.offset:0))
					+(isRotated?0:lineSpace);//padding

				minSize.height=Math.min(me.maxHeight,minSize.height+labelHeight+tickPadding);

				varoffsetLeft=me.getPixelForTick(0)-me.left;
				varoffsetRight=me.right-me.getPixelForTick(me.getTicks().length-1);
				varpaddingLeft,paddingRight;

				//Ensurethatourticksarealwaysinsidethecanvas.Whenrotated,ticksarerightaligned
				//whichmeansthattherightpaddingisdominatedbythefontheight
				if(isRotated){
					paddingLeft=isBottom?
						cosRotation*firstLabelSize.width+sinRotation*firstLabelSize.offset:
						sinRotation*(firstLabelSize.height-firstLabelSize.offset);
					paddingRight=isBottom?
						sinRotation*(lastLabelSize.height-lastLabelSize.offset):
						cosRotation*lastLabelSize.width+sinRotation*lastLabelSize.offset;
				}else{
					paddingLeft=firstLabelSize.width/2;
					paddingRight=lastLabelSize.width/2;
				}

				//Adjustpaddingtakingintoaccountchangesinoffsets
				//andadd3pxtomoveawayfromcanvasedges
				me.paddingLeft=Math.max((paddingLeft-offsetLeft)*me.width/(me.width-offsetLeft),0)+3;
				me.paddingRight=Math.max((paddingRight-offsetRight)*me.width/(me.width-offsetRight),0)+3;
			}else{
				//Averticalaxisismoreconstrainedbythewidth.Labelsarethe
				//dominantfactorhere,sogetthatlengthfirstandaccountforpadding
				varlabelWidth=tickOpts.mirror?0:
					//uselineSpaceforconsistencywithhorizontalaxis
					//tickPaddingisnotimplementedforhorizontal
					widestLabelSize.width+tickPadding+lineSpace;

				minSize.width=Math.min(me.maxWidth,minSize.width+labelWidth);

				me.paddingTop=firstLabelSize.height/2;
				me.paddingBottom=lastLabelSize.height/2;
			}
		}

		me.handleMargins();

		if(isHorizontal){
			me.width=me._length=chart.width-me.margins.left-me.margins.right;
			me.height=minSize.height;
		}else{
			me.width=minSize.width;
			me.height=me._length=chart.height-me.margins.top-me.margins.bottom;
		}
	},

	/**
	*Handlemarginsandpaddinginteractions
	*@private
	*/
	handleMargins:function(){
		varme=this;
		if(me.margins){
			me.margins.left=Math.max(me.paddingLeft,me.margins.left);
			me.margins.top=Math.max(me.paddingTop,me.margins.top);
			me.margins.right=Math.max(me.paddingRight,me.margins.right);
			me.margins.bottom=Math.max(me.paddingBottom,me.margins.bottom);
		}
	},

	afterFit:function(){
		helpers$1.callback(this.options.afterFit,[this]);
	},

	//SharedMethods
	isHorizontal:function(){
		varpos=this.options.position;
		returnpos==='top'||pos==='bottom';
	},
	isFullWidth:function(){
		returnthis.options.fullWidth;
	},

	//Getthecorrectvalue.NaNbadinputs,Ifthevaluetypeisobjectgetthexorybasedonwhetherwearehorizontalornot
	getRightValue:function(rawValue){
		//Nullandundefinedvaluesfirst
		if(isNullOrUndef(rawValue)){
			returnNaN;
		}
		//isNaN(object)returnstrue,somakesureNaNischeckingforanumber;DiscardInfinitevalues
		if((typeofrawValue==='number'||rawValueinstanceofNumber)&&!isFinite(rawValue)){
			returnNaN;
		}

		//Ifitisinfactanobject,diveinonemorelevel
		if(rawValue){
			if(this.isHorizontal()){
				if(rawValue.x!==undefined){
					returnthis.getRightValue(rawValue.x);
				}
			}elseif(rawValue.y!==undefined){
				returnthis.getRightValue(rawValue.y);
			}
		}

		//Valueisgood,returnit
		returnrawValue;
	},

	_convertTicksToLabels:function(ticks){
		varme=this;
		varlabels,i,ilen;

		me.ticks=ticks.map(function(tick){
			returntick.value;
		});

		me.beforeTickToLabelConversion();

		//NewimplementationsshouldreturntheformattedticklabelsbutforBACKWARD
		//COMPAT,westillsupportnoreturn(`this.ticks`internallychangedbycalling
		//thismethodandsupposedtocontainonlystringvalues).
		labels=me.convertTicksToLabels(ticks)||me.ticks;

		me.afterTickToLabelConversion();

		//BACKWARDCOMPAT:synchronize`_ticks`withlabels(sopotentially`this.ticks`)
		for(i=0,ilen=ticks.length;i<ilen;++i){
			ticks[i].label=labels[i];
		}

		returnlabels;
	},

	/**
	*@private
	*/
	_getLabelSizes:function(){
		varme=this;
		varlabelSizes=me._labelSizes;

		if(!labelSizes){
			me._labelSizes=labelSizes=computeLabelSizes(me.ctx,parseTickFontOptions(me.options.ticks),me.getTicks(),me.longestTextCache);
			me.longestLabelWidth=labelSizes.widest.width;
		}

		returnlabelSizes;
	},

	/**
	*@private
	*/
	_parseValue:function(value){
		varstart,end,min,max;

		if(isArray(value)){
			start=+this.getRightValue(value[0]);
			end=+this.getRightValue(value[1]);
			min=Math.min(start,end);
			max=Math.max(start,end);
		}else{
			value=+this.getRightValue(value);
			start=undefined;
			end=value;
			min=value;
			max=value;
		}

		return{
			min:min,
			max:max,
			start:start,
			end:end
		};
	},

	/**
	*@private
	*/
	_getScaleLabel:function(rawValue){
		varv=this._parseValue(rawValue);
		if(v.start!==undefined){
			return'['+v.start+','+v.end+']';
		}

		return+this.getRightValue(rawValue);
	},

	/**
	*Usedtogetthevaluetodisplayinthetooltipforthedataatthegivenindex
	*@paramindex
	*@paramdatasetIndex
	*/
	getLabelForIndex:helpers$1.noop,

	/**
	*Returnsthelocationofthegivendatapoint.Valuecaneitherbeanindexoranumericalvalue
	*Thecoordinate(0,0)isattheupper-leftcornerofthecanvas
	*@paramvalue
	*@paramindex
	*@paramdatasetIndex
	*/
	getPixelForValue:helpers$1.noop,

	/**
	*Usedtogetthedatavaluefromagivenpixel.ThisistheinverseofgetPixelForValue
	*Thecoordinate(0,0)isattheupper-leftcornerofthecanvas
	*@parampixel
	*/
	getValueForPixel:helpers$1.noop,

	/**
	*Returnsthelocationofthetickatthegivenindex
	*Thecoordinate(0,0)isattheupper-leftcornerofthecanvas
	*/
	getPixelForTick:function(index){
		varme=this;
		varoffset=me.options.offset;
		varnumTicks=me._ticks.length;
		vartickWidth=1/Math.max(numTicks-(offset?0:1),1);

		returnindex<0||index>numTicks-1
			?null
			:me.getPixelForDecimal(index*tickWidth+(offset?tickWidth/2:0));
	},

	/**
	*Utilityforgettingthepixellocationofapercentageofscale
	*Thecoordinate(0,0)isattheupper-leftcornerofthecanvas
	*/
	getPixelForDecimal:function(decimal){
		varme=this;

		if(me._reversePixels){
			decimal=1-decimal;
		}

		returnme._startPixel+decimal*me._length;
	},

	getDecimalForPixel:function(pixel){
		vardecimal=(pixel-this._startPixel)/this._length;
		returnthis._reversePixels?1-decimal:decimal;
	},

	/**
	*Returnsthepixelfortheminimumchartvalue
	*Thecoordinate(0,0)isattheupper-leftcornerofthecanvas
	*/
	getBasePixel:function(){
		returnthis.getPixelForValue(this.getBaseValue());
	},

	getBaseValue:function(){
		varme=this;
		varmin=me.min;
		varmax=me.max;

		returnme.beginAtZero?0:
			min<0&&max<0?max:
			min>0&&max>0?min:
			0;
	},

	/**
	*Returnsasubsetoftickstobeplottedtoavoidoverlappinglabels.
	*@private
	*/
	_autoSkip:function(ticks){
		varme=this;
		vartickOpts=me.options.ticks;
		varaxisLength=me._length;
		varticksLimit=tickOpts.maxTicksLimit||axisLength/me._tickSize()+1;
		varmajorIndices=tickOpts.major.enabled?getMajorIndices(ticks):[];
		varnumMajorIndices=majorIndices.length;
		varfirst=majorIndices[0];
		varlast=majorIndices[numMajorIndices-1];
		vari,ilen,spacing,avgMajorSpacing;

		//Iftherearetoomanymajortickstodisplaythemall
		if(numMajorIndices>ticksLimit){
			skipMajors(ticks,majorIndices,numMajorIndices/ticksLimit);
			returnnonSkipped(ticks);
		}

		spacing=calculateSpacing(majorIndices,ticks,axisLength,ticksLimit);

		if(numMajorIndices>0){
			for(i=0,ilen=numMajorIndices-1;i<ilen;i++){
				skip(ticks,spacing,majorIndices[i],majorIndices[i+1]);
			}
			avgMajorSpacing=numMajorIndices>1?(last-first)/(numMajorIndices-1):null;
			skip(ticks,spacing,helpers$1.isNullOrUndef(avgMajorSpacing)?0:first-avgMajorSpacing,first);
			skip(ticks,spacing,last,helpers$1.isNullOrUndef(avgMajorSpacing)?ticks.length:last+avgMajorSpacing);
			returnnonSkipped(ticks);
		}
		skip(ticks,spacing);
		returnnonSkipped(ticks);
	},

	/**
	*@private
	*/
	_tickSize:function(){
		varme=this;
		varoptionTicks=me.options.ticks;

		//Calculatespaceneededbylabelinaxisdirection.
		varrot=helpers$1.toRadians(me.labelRotation);
		varcos=Math.abs(Math.cos(rot));
		varsin=Math.abs(Math.sin(rot));

		varlabelSizes=me._getLabelSizes();
		varpadding=optionTicks.autoSkipPadding||0;
		varw=labelSizes?labelSizes.widest.width+padding:0;
		varh=labelSizes?labelSizes.highest.height+padding:0;

		//Calculatespaceneededfor1tickinaxisdirection.
		returnme.isHorizontal()
			?h*cos>w*sin?w/cos:h/sin
			:h*sin<w*cos?h/cos:w/sin;
	},

	/**
	*@private
	*/
	_isVisible:function(){
		varme=this;
		varchart=me.chart;
		vardisplay=me.options.display;
		vari,ilen,meta;

		if(display!=='auto'){
			return!!display;
		}

		//When'auto',thescaleisvisibleifatleastoneassociateddatasetisvisible.
		for(i=0,ilen=chart.data.datasets.length;i<ilen;++i){
			if(chart.isDatasetVisible(i)){
				meta=chart.getDatasetMeta(i);
				if(meta.xAxisID===me.id||meta.yAxisID===me.id){
					returntrue;
				}
			}
		}

		returnfalse;
	},

	/**
	*@private
	*/
	_computeGridLineItems:function(chartArea){
		varme=this;
		varchart=me.chart;
		varoptions=me.options;
		vargridLines=options.gridLines;
		varposition=options.position;
		varoffsetGridLines=gridLines.offsetGridLines;
		varisHorizontal=me.isHorizontal();
		varticks=me._ticksToDraw;
		varticksLength=ticks.length+(offsetGridLines?1:0);

		vartl=getTickMarkLength(gridLines);
		varitems=[];
		varaxisWidth=gridLines.drawBorder?valueAtIndexOrDefault(gridLines.lineWidth,0,0):0;
		varaxisHalfWidth=axisWidth/2;
		varalignPixel=helpers$1._alignPixel;
		varalignBorderValue=function(pixel){
			returnalignPixel(chart,pixel,axisWidth);
		};
		varborderValue,i,tick,lineValue,alignedLineValue;
		vartx1,ty1,tx2,ty2,x1,y1,x2,y2,lineWidth,lineColor,borderDash,borderDashOffset;

		if(position==='top'){
			borderValue=alignBorderValue(me.bottom);
			ty1=me.bottom-tl;
			ty2=borderValue-axisHalfWidth;
			y1=alignBorderValue(chartArea.top)+axisHalfWidth;
			y2=chartArea.bottom;
		}elseif(position==='bottom'){
			borderValue=alignBorderValue(me.top);
			y1=chartArea.top;
			y2=alignBorderValue(chartArea.bottom)-axisHalfWidth;
			ty1=borderValue+axisHalfWidth;
			ty2=me.top+tl;
		}elseif(position==='left'){
			borderValue=alignBorderValue(me.right);
			tx1=me.right-tl;
			tx2=borderValue-axisHalfWidth;
			x1=alignBorderValue(chartArea.left)+axisHalfWidth;
			x2=chartArea.right;
		}else{
			borderValue=alignBorderValue(me.left);
			x1=chartArea.left;
			x2=alignBorderValue(chartArea.right)-axisHalfWidth;
			tx1=borderValue+axisHalfWidth;
			tx2=me.left+tl;
		}

		for(i=0;i<ticksLength;++i){
			tick=ticks[i]||{};

			//autoskipperskippedthistick(#4635)
			if(isNullOrUndef(tick.label)&&i<ticks.length){
				continue;
			}

			if(i===me.zeroLineIndex&&options.offset===offsetGridLines){
				//Drawthefirstindexspecially
				lineWidth=gridLines.zeroLineWidth;
				lineColor=gridLines.zeroLineColor;
				borderDash=gridLines.zeroLineBorderDash||[];
				borderDashOffset=gridLines.zeroLineBorderDashOffset||0.0;
			}else{
				lineWidth=valueAtIndexOrDefault(gridLines.lineWidth,i,1);
				lineColor=valueAtIndexOrDefault(gridLines.color,i,'rgba(0,0,0,0.1)');
				borderDash=gridLines.borderDash||[];
				borderDashOffset=gridLines.borderDashOffset||0.0;
			}

			lineValue=getPixelForGridLine(me,tick._index||i,offsetGridLines);

			//Skipifthepixelisoutoftherange
			if(lineValue===undefined){
				continue;
			}

			alignedLineValue=alignPixel(chart,lineValue,lineWidth);

			if(isHorizontal){
				tx1=tx2=x1=x2=alignedLineValue;
			}else{
				ty1=ty2=y1=y2=alignedLineValue;
			}

			items.push({
				tx1:tx1,
				ty1:ty1,
				tx2:tx2,
				ty2:ty2,
				x1:x1,
				y1:y1,
				x2:x2,
				y2:y2,
				width:lineWidth,
				color:lineColor,
				borderDash:borderDash,
				borderDashOffset:borderDashOffset,
			});
		}

		items.ticksLength=ticksLength;
		items.borderValue=borderValue;

		returnitems;
	},

	/**
	*@private
	*/
	_computeLabelItems:function(){
		varme=this;
		varoptions=me.options;
		varoptionTicks=options.ticks;
		varposition=options.position;
		varisMirrored=optionTicks.mirror;
		varisHorizontal=me.isHorizontal();
		varticks=me._ticksToDraw;
		varfonts=parseTickFontOptions(optionTicks);
		vartickPadding=optionTicks.padding;
		vartl=getTickMarkLength(options.gridLines);
		varrotation=-helpers$1.toRadians(me.labelRotation);
		varitems=[];
		vari,ilen,tick,label,x,y,textAlign,pixel,font,lineHeight,lineCount,textOffset;

		if(position==='top'){
			y=me.bottom-tl-tickPadding;
			textAlign=!rotation?'center':'left';
		}elseif(position==='bottom'){
			y=me.top+tl+tickPadding;
			textAlign=!rotation?'center':'right';
		}elseif(position==='left'){
			x=me.right-(isMirrored?0:tl)-tickPadding;
			textAlign=isMirrored?'left':'right';
		}else{
			x=me.left+(isMirrored?0:tl)+tickPadding;
			textAlign=isMirrored?'right':'left';
		}

		for(i=0,ilen=ticks.length;i<ilen;++i){
			tick=ticks[i];
			label=tick.label;

			//autoskipperskippedthistick(#4635)
			if(isNullOrUndef(label)){
				continue;
			}

			pixel=me.getPixelForTick(tick._index||i)+optionTicks.labelOffset;
			font=tick.major?fonts.major:fonts.minor;
			lineHeight=font.lineHeight;
			lineCount=isArray(label)?label.length:1;

			if(isHorizontal){
				x=pixel;
				textOffset=position==='top'
					?((!rotation?0.5:1)-lineCount)*lineHeight
					:(!rotation?0.5:0)*lineHeight;
			}else{
				y=pixel;
				textOffset=(1-lineCount)*lineHeight/2;
			}

			items.push({
				x:x,
				y:y,
				rotation:rotation,
				label:label,
				font:font,
				textOffset:textOffset,
				textAlign:textAlign
			});
		}

		returnitems;
	},

	/**
	*@private
	*/
	_drawGrid:function(chartArea){
		varme=this;
		vargridLines=me.options.gridLines;

		if(!gridLines.display){
			return;
		}

		varctx=me.ctx;
		varchart=me.chart;
		varalignPixel=helpers$1._alignPixel;
		varaxisWidth=gridLines.drawBorder?valueAtIndexOrDefault(gridLines.lineWidth,0,0):0;
		varitems=me._gridLineItems||(me._gridLineItems=me._computeGridLineItems(chartArea));
		varwidth,color,i,ilen,item;

		for(i=0,ilen=items.length;i<ilen;++i){
			item=items[i];
			width=item.width;
			color=item.color;

			if(width&&color){
				ctx.save();
				ctx.lineWidth=width;
				ctx.strokeStyle=color;
				if(ctx.setLineDash){
					ctx.setLineDash(item.borderDash);
					ctx.lineDashOffset=item.borderDashOffset;
				}

				ctx.beginPath();

				if(gridLines.drawTicks){
					ctx.moveTo(item.tx1,item.ty1);
					ctx.lineTo(item.tx2,item.ty2);
				}

				if(gridLines.drawOnChartArea){
					ctx.moveTo(item.x1,item.y1);
					ctx.lineTo(item.x2,item.y2);
				}

				ctx.stroke();
				ctx.restore();
			}
		}

		if(axisWidth){
			//Drawthelineattheedgeoftheaxis
			varfirstLineWidth=axisWidth;
			varlastLineWidth=valueAtIndexOrDefault(gridLines.lineWidth,items.ticksLength-1,1);
			varborderValue=items.borderValue;
			varx1,x2,y1,y2;

			if(me.isHorizontal()){
				x1=alignPixel(chart,me.left,firstLineWidth)-firstLineWidth/2;
				x2=alignPixel(chart,me.right,lastLineWidth)+lastLineWidth/2;
				y1=y2=borderValue;
			}else{
				y1=alignPixel(chart,me.top,firstLineWidth)-firstLineWidth/2;
				y2=alignPixel(chart,me.bottom,lastLineWidth)+lastLineWidth/2;
				x1=x2=borderValue;
			}

			ctx.lineWidth=axisWidth;
			ctx.strokeStyle=valueAtIndexOrDefault(gridLines.color,0);
			ctx.beginPath();
			ctx.moveTo(x1,y1);
			ctx.lineTo(x2,y2);
			ctx.stroke();
		}
	},

	/**
	*@private
	*/
	_drawLabels:function(){
		varme=this;
		varoptionTicks=me.options.ticks;

		if(!optionTicks.display){
			return;
		}

		varctx=me.ctx;
		varitems=me._labelItems||(me._labelItems=me._computeLabelItems());
		vari,j,ilen,jlen,item,tickFont,label,y;

		for(i=0,ilen=items.length;i<ilen;++i){
			item=items[i];
			tickFont=item.font;

			//Makesurewedrawtextinthecorrectcolorandfont
			ctx.save();
			ctx.translate(item.x,item.y);
			ctx.rotate(item.rotation);
			ctx.font=tickFont.string;
			ctx.fillStyle=tickFont.color;
			ctx.textBaseline='middle';
			ctx.textAlign=item.textAlign;

			label=item.label;
			y=item.textOffset;
			if(isArray(label)){
				for(j=0,jlen=label.length;j<jlen;++j){
					//Wejustmakesurethemultilineelementisastringhere..
					ctx.fillText(''+label[j],0,y);
					y+=tickFont.lineHeight;
				}
			}else{
				ctx.fillText(label,0,y);
			}
			ctx.restore();
		}
	},

	/**
	*@private
	*/
	_drawTitle:function(){
		varme=this;
		varctx=me.ctx;
		varoptions=me.options;
		varscaleLabel=options.scaleLabel;

		if(!scaleLabel.display){
			return;
		}

		varscaleLabelFontColor=valueOrDefault$a(scaleLabel.fontColor,core_defaults.global.defaultFontColor);
		varscaleLabelFont=helpers$1.options._parseFont(scaleLabel);
		varscaleLabelPadding=helpers$1.options.toPadding(scaleLabel.padding);
		varhalfLineHeight=scaleLabelFont.lineHeight/2;
		varposition=options.position;
		varrotation=0;
		varscaleLabelX,scaleLabelY;

		if(me.isHorizontal()){
			scaleLabelX=me.left+me.width/2;//midpointofthewidth
			scaleLabelY=position==='bottom'
				?me.bottom-halfLineHeight-scaleLabelPadding.bottom
				:me.top+halfLineHeight+scaleLabelPadding.top;
		}else{
			varisLeft=position==='left';
			scaleLabelX=isLeft
				?me.left+halfLineHeight+scaleLabelPadding.top
				:me.right-halfLineHeight-scaleLabelPadding.top;
			scaleLabelY=me.top+me.height/2;
			rotation=isLeft?-0.5*Math.PI:0.5*Math.PI;
		}

		ctx.save();
		ctx.translate(scaleLabelX,scaleLabelY);
		ctx.rotate(rotation);
		ctx.textAlign='center';
		ctx.textBaseline='middle';
		ctx.fillStyle=scaleLabelFontColor;//renderincorrectcolour
		ctx.font=scaleLabelFont.string;
		ctx.fillText(scaleLabel.labelString,0,0);
		ctx.restore();
	},

	draw:function(chartArea){
		varme=this;

		if(!me._isVisible()){
			return;
		}

		me._drawGrid(chartArea);
		me._drawTitle();
		me._drawLabels();
	},

	/**
	*@private
	*/
	_layers:function(){
		varme=this;
		varopts=me.options;
		vartz=opts.ticks&&opts.ticks.z||0;
		vargz=opts.gridLines&&opts.gridLines.z||0;

		if(!me._isVisible()||tz===gz||me.draw!==me._draw){
			//backwardcompatibility:drawhasbeenoverriddenbycustomscale
			return[{
				z:tz,
				draw:function(){
					me.draw.apply(me,arguments);
				}
			}];
		}

		return[{
			z:gz,
			draw:function(){
				me._drawGrid.apply(me,arguments);
				me._drawTitle.apply(me,arguments);
			}
		},{
			z:tz,
			draw:function(){
				me._drawLabels.apply(me,arguments);
			}
		}];
	},

	/**
	*@private
	*/
	_getMatchingVisibleMetas:function(type){
		varme=this;
		varisHorizontal=me.isHorizontal();
		returnme.chart._getSortedVisibleDatasetMetas()
			.filter(function(meta){
				return(!type||meta.type===type)
					&&(isHorizontal?meta.xAxisID===me.id:meta.yAxisID===me.id);
			});
	}
});

Scale.prototype._draw=Scale.prototype.draw;

varcore_scale=Scale;

varisNullOrUndef$1=helpers$1.isNullOrUndef;

vardefaultConfig={
	position:'bottom'
};

varscale_category=core_scale.extend({
	determineDataLimits:function(){
		varme=this;
		varlabels=me._getLabels();
		varticksOpts=me.options.ticks;
		varmin=ticksOpts.min;
		varmax=ticksOpts.max;
		varminIndex=0;
		varmaxIndex=labels.length-1;
		varfindIndex;

		if(min!==undefined){
			//userspecifiedminvalue
			findIndex=labels.indexOf(min);
			if(findIndex>=0){
				minIndex=findIndex;
			}
		}

		if(max!==undefined){
			//userspecifiedmaxvalue
			findIndex=labels.indexOf(max);
			if(findIndex>=0){
				maxIndex=findIndex;
			}
		}

		me.minIndex=minIndex;
		me.maxIndex=maxIndex;
		me.min=labels[minIndex];
		me.max=labels[maxIndex];
	},

	buildTicks:function(){
		varme=this;
		varlabels=me._getLabels();
		varminIndex=me.minIndex;
		varmaxIndex=me.maxIndex;

		//Ifweareviewingsomesubsetoflabels,slicetheoriginalarray
		me.ticks=(minIndex===0&&maxIndex===labels.length-1)?labels:labels.slice(minIndex,maxIndex+1);
	},

	getLabelForIndex:function(index,datasetIndex){
		varme=this;
		varchart=me.chart;

		if(chart.getDatasetMeta(datasetIndex).controller._getValueScaleId()===me.id){
			returnme.getRightValue(chart.data.datasets[datasetIndex].data[index]);
		}

		returnme._getLabels()[index];
	},

	_configure:function(){
		varme=this;
		varoffset=me.options.offset;
		varticks=me.ticks;

		core_scale.prototype._configure.call(me);

		if(!me.isHorizontal()){
			//Forbackwardcompatibility,verticalcategoryscalereverseisinverted.
			me._reversePixels=!me._reversePixels;
		}

		if(!ticks){
			return;
		}

		me._startValue=me.minIndex-(offset?0.5:0);
		me._valueRange=Math.max(ticks.length-(offset?0:1),1);
	},

	//Usedtogetdatavaluelocations. Valuecaneitherbeanindexoranumericalvalue
	getPixelForValue:function(value,index,datasetIndex){
		varme=this;
		varvalueCategory,labels,idx;

		if(!isNullOrUndef$1(index)&&!isNullOrUndef$1(datasetIndex)){
			value=me.chart.data.datasets[datasetIndex].data[index];
		}

		//Ifvalueisadataobject,thenindexistheindexinthedataarray,
		//nottheindexofthescale.Weneedtochangethat.
		if(!isNullOrUndef$1(value)){
			valueCategory=me.isHorizontal()?value.x:value.y;
		}
		if(valueCategory!==undefined||(value!==undefined&&isNaN(index))){
			labels=me._getLabels();
			value=helpers$1.valueOrDefault(valueCategory,value);
			idx=labels.indexOf(value);
			index=idx!==-1?idx:index;
			if(isNaN(index)){
				index=value;
			}
		}
		returnme.getPixelForDecimal((index-me._startValue)/me._valueRange);
	},

	getPixelForTick:function(index){
		varticks=this.ticks;
		returnindex<0||index>ticks.length-1
			?null
			:this.getPixelForValue(ticks[index],index+this.minIndex);
	},

	getValueForPixel:function(pixel){
		varme=this;
		varvalue=Math.round(me._startValue+me.getDecimalForPixel(pixel)*me._valueRange);
		returnMath.min(Math.max(value,0),me.ticks.length-1);
	},

	getBasePixel:function(){
		returnthis.bottom;
	}
});

//INTERNAL:staticdefaultoptions,registeredinsrc/index.js
var_defaults=defaultConfig;
scale_category._defaults=_defaults;

varnoop=helpers$1.noop;
varisNullOrUndef$2=helpers$1.isNullOrUndef;

/**
 *Generateasetoflinearticks
 *@paramgenerationOptionstheoptionsusedtogeneratetheticks
 *@paramdataRangetherangeofthedata
 *@returns{number[]}arrayoftickvalues
 */
functiongenerateTicks(generationOptions,dataRange){
	varticks=[];
	//Togeta"nice"valueforthetickspacing,wewillusetheappropriatelynamed
	//"nicenumber"algorithm.Seehttps://stackoverflow.com/questions/8506881/nice-label-algorithm-for-charts-with-minimum-ticks
	//fordetails.

	varMIN_SPACING=1e-14;
	varstepSize=generationOptions.stepSize;
	varunit=stepSize||1;
	varmaxNumSpaces=generationOptions.maxTicks-1;
	varmin=generationOptions.min;
	varmax=generationOptions.max;
	varprecision=generationOptions.precision;
	varrmin=dataRange.min;
	varrmax=dataRange.max;
	varspacing=helpers$1.niceNum((rmax-rmin)/maxNumSpaces/unit)*unit;
	varfactor,niceMin,niceMax,numSpaces;

	//BeyondMIN_SPACINGfloatingpointnumbersbeingtoloseprecision
	//suchthatwecan'tdothemathnecessarytogenerateticks
	if(spacing<MIN_SPACING&&isNullOrUndef$2(min)&&isNullOrUndef$2(max)){
		return[rmin,rmax];
	}

	numSpaces=Math.ceil(rmax/spacing)-Math.floor(rmin/spacing);
	if(numSpaces>maxNumSpaces){
		//IfthecalculatednumofspacesexceedsmaxNumSpaces,recalculateit
		spacing=helpers$1.niceNum(numSpaces*spacing/maxNumSpaces/unit)*unit;
	}

	if(stepSize||isNullOrUndef$2(precision)){
		//Ifaprecisionisnotspecified,calculatefactorbasedonspacing
		factor=Math.pow(10,helpers$1._decimalPlaces(spacing));
	}else{
		//Iftheuserspecifiedaprecision,roundtothatnumberofdecimalplaces
		factor=Math.pow(10,precision);
		spacing=Math.ceil(spacing*factor)/factor;
	}

	niceMin=Math.floor(rmin/spacing)*spacing;
	niceMax=Math.ceil(rmax/spacing)*spacing;

	//Ifmin,maxandstepSizeissetandtheymakeanevenlyspacedscaleuseit.
	if(stepSize){
		//Ifveryclosetoourwholenumber,useit.
		if(!isNullOrUndef$2(min)&&helpers$1.almostWhole(min/spacing,spacing/1000)){
			niceMin=min;
		}
		if(!isNullOrUndef$2(max)&&helpers$1.almostWhole(max/spacing,spacing/1000)){
			niceMax=max;
		}
	}

	numSpaces=(niceMax-niceMin)/spacing;
	//Ifveryclosetoourroundedvalue,useit.
	if(helpers$1.almostEquals(numSpaces,Math.round(numSpaces),spacing/1000)){
		numSpaces=Math.round(numSpaces);
	}else{
		numSpaces=Math.ceil(numSpaces);
	}

	niceMin=Math.round(niceMin*factor)/factor;
	niceMax=Math.round(niceMax*factor)/factor;
	ticks.push(isNullOrUndef$2(min)?niceMin:min);
	for(varj=1;j<numSpaces;++j){
		ticks.push(Math.round((niceMin+j*spacing)*factor)/factor);
	}
	ticks.push(isNullOrUndef$2(max)?niceMax:max);

	returnticks;
}

varscale_linearbase=core_scale.extend({
	getRightValue:function(value){
		if(typeofvalue==='string'){
			return+value;
		}
		returncore_scale.prototype.getRightValue.call(this,value);
	},

	handleTickRangeOptions:function(){
		varme=this;
		varopts=me.options;
		vartickOpts=opts.ticks;

		//Ifweareforcingittobeginat0,but0willalreadyberenderedonthechart,
		//donothingsincethatwouldmakethechartweird.Iftheuserreallywantsaweirdchart
		//axis,theycanmanuallyoverrideit
		if(tickOpts.beginAtZero){
			varminSign=helpers$1.sign(me.min);
			varmaxSign=helpers$1.sign(me.max);

			if(minSign<0&&maxSign<0){
				//movethetopupto0
				me.max=0;
			}elseif(minSign>0&&maxSign>0){
				//movethebottomdownto0
				me.min=0;
			}
		}

		varsetMin=tickOpts.min!==undefined||tickOpts.suggestedMin!==undefined;
		varsetMax=tickOpts.max!==undefined||tickOpts.suggestedMax!==undefined;

		if(tickOpts.min!==undefined){
			me.min=tickOpts.min;
		}elseif(tickOpts.suggestedMin!==undefined){
			if(me.min===null){
				me.min=tickOpts.suggestedMin;
			}else{
				me.min=Math.min(me.min,tickOpts.suggestedMin);
			}
		}

		if(tickOpts.max!==undefined){
			me.max=tickOpts.max;
		}elseif(tickOpts.suggestedMax!==undefined){
			if(me.max===null){
				me.max=tickOpts.suggestedMax;
			}else{
				me.max=Math.max(me.max,tickOpts.suggestedMax);
			}
		}

		if(setMin!==setMax){
			//Wesettheminorthemaxbutnotboth.
			//Soensurethatourrangeisgood
			//Invertedor0lengthrangecanhappenwhen
			//ticks.minisset,andnodatasetsarevisible
			if(me.min>=me.max){
				if(setMin){
					me.max=me.min+1;
				}else{
					me.min=me.max-1;
				}
			}
		}

		if(me.min===me.max){
			me.max++;

			if(!tickOpts.beginAtZero){
				me.min--;
			}
		}
	},

	getTickLimit:function(){
		varme=this;
		vartickOpts=me.options.ticks;
		varstepSize=tickOpts.stepSize;
		varmaxTicksLimit=tickOpts.maxTicksLimit;
		varmaxTicks;

		if(stepSize){
			maxTicks=Math.ceil(me.max/stepSize)-Math.floor(me.min/stepSize)+1;
		}else{
			maxTicks=me._computeTickLimit();
			maxTicksLimit=maxTicksLimit||11;
		}

		if(maxTicksLimit){
			maxTicks=Math.min(maxTicksLimit,maxTicks);
		}

		returnmaxTicks;
	},

	_computeTickLimit:function(){
		returnNumber.POSITIVE_INFINITY;
	},

	handleDirectionalChanges:noop,

	buildTicks:function(){
		varme=this;
		varopts=me.options;
		vartickOpts=opts.ticks;

		//Figureoutwhatthemaxnumberoftickswecansupportitisbasedonthesizeof
		//theaxisarea.Fornow,wesaythattheminimumtickspacinginpixelsmustbe40
		//Wealsolimitthemaximumnumberofticksto11whichgivesanice10squareson
		//thegraph.Makesurewealwayshaveatleast2ticks
		varmaxTicks=me.getTickLimit();
		maxTicks=Math.max(2,maxTicks);

		varnumericGeneratorOptions={
			maxTicks:maxTicks,
			min:tickOpts.min,
			max:tickOpts.max,
			precision:tickOpts.precision,
			stepSize:helpers$1.valueOrDefault(tickOpts.fixedStepSize,tickOpts.stepSize)
		};
		varticks=me.ticks=generateTicks(numericGeneratorOptions,me);

		me.handleDirectionalChanges();

		//Atthispoint,weneedtoupdateourmaxandmingiventhetickvaluessincewehaveexpandedthe
		//rangeofthescale
		me.max=helpers$1.max(ticks);
		me.min=helpers$1.min(ticks);

		if(tickOpts.reverse){
			ticks.reverse();

			me.start=me.max;
			me.end=me.min;
		}else{
			me.start=me.min;
			me.end=me.max;
		}
	},

	convertTicksToLabels:function(){
		varme=this;
		me.ticksAsNumbers=me.ticks.slice();
		me.zeroLineIndex=me.ticks.indexOf(0);

		core_scale.prototype.convertTicksToLabels.call(me);
	},

	_configure:function(){
		varme=this;
		varticks=me.getTicks();
		varstart=me.min;
		varend=me.max;
		varoffset;

		core_scale.prototype._configure.call(me);

		if(me.options.offset&&ticks.length){
			offset=(end-start)/Math.max(ticks.length-1,1)/2;
			start-=offset;
			end+=offset;
		}
		me._startValue=start;
		me._endValue=end;
		me._valueRange=end-start;
	}
});

vardefaultConfig$1={
	position:'left',
	ticks:{
		callback:core_ticks.formatters.linear
	}
};

varDEFAULT_MIN=0;
varDEFAULT_MAX=1;

functiongetOrCreateStack(stacks,stacked,meta){
	varkey=[
		meta.type,
		//wehaveaseparatestackforstack=undefineddatasetswhentheopts.stackedisundefined
		stacked===undefined&&meta.stack===undefined?meta.index:'',
		meta.stack
	].join('.');

	if(stacks[key]===undefined){
		stacks[key]={
			pos:[],
			neg:[]
		};
	}

	returnstacks[key];
}

functionstackData(scale,stacks,meta,data){
	varopts=scale.options;
	varstacked=opts.stacked;
	varstack=getOrCreateStack(stacks,stacked,meta);
	varpos=stack.pos;
	varneg=stack.neg;
	varilen=data.length;
	vari,value;

	for(i=0;i<ilen;++i){
		value=scale._parseValue(data[i]);
		if(isNaN(value.min)||isNaN(value.max)||meta.data[i].hidden){
			continue;
		}

		pos[i]=pos[i]||0;
		neg[i]=neg[i]||0;

		if(opts.relativePoints){
			pos[i]=100;
		}elseif(value.min<0||value.max<0){
			neg[i]+=value.min;
		}else{
			pos[i]+=value.max;
		}
	}
}

functionupdateMinMax(scale,meta,data){
	varilen=data.length;
	vari,value;

	for(i=0;i<ilen;++i){
		value=scale._parseValue(data[i]);
		if(isNaN(value.min)||isNaN(value.max)||meta.data[i].hidden){
			continue;
		}

		scale.min=Math.min(scale.min,value.min);
		scale.max=Math.max(scale.max,value.max);
	}
}

varscale_linear=scale_linearbase.extend({
	determineDataLimits:function(){
		varme=this;
		varopts=me.options;
		varchart=me.chart;
		vardatasets=chart.data.datasets;
		varmetasets=me._getMatchingVisibleMetas();
		varhasStacks=opts.stacked;
		varstacks={};
		varilen=metasets.length;
		vari,meta,data,values;

		me.min=Number.POSITIVE_INFINITY;
		me.max=Number.NEGATIVE_INFINITY;

		if(hasStacks===undefined){
			for(i=0;!hasStacks&&i<ilen;++i){
				meta=metasets[i];
				hasStacks=meta.stack!==undefined;
			}
		}

		for(i=0;i<ilen;++i){
			meta=metasets[i];
			data=datasets[meta.index].data;
			if(hasStacks){
				stackData(me,stacks,meta,data);
			}else{
				updateMinMax(me,meta,data);
			}
		}

		helpers$1.each(stacks,function(stackValues){
			values=stackValues.pos.concat(stackValues.neg);
			me.min=Math.min(me.min,helpers$1.min(values));
			me.max=Math.max(me.max,helpers$1.max(values));
		});

		me.min=helpers$1.isFinite(me.min)&&!isNaN(me.min)?me.min:DEFAULT_MIN;
		me.max=helpers$1.isFinite(me.max)&&!isNaN(me.max)?me.max:DEFAULT_MAX;

		//Commonbaseimplementationtohandleticks.min,ticks.max,ticks.beginAtZero
		me.handleTickRangeOptions();
	},

	//Returnsthemaximumnumberofticksbasedonthescaledimension
	_computeTickLimit:function(){
		varme=this;
		vartickFont;

		if(me.isHorizontal()){
			returnMath.ceil(me.width/40);
		}
		tickFont=helpers$1.options._parseFont(me.options.ticks);
		returnMath.ceil(me.height/tickFont.lineHeight);
	},

	//Calledaftertheticksarebuilt.Weneed
	handleDirectionalChanges:function(){
		if(!this.isHorizontal()){
			//Weareinaverticalorientation.Thetopvalueisthehighest.Soreversethearray
			this.ticks.reverse();
		}
	},

	getLabelForIndex:function(index,datasetIndex){
		returnthis._getScaleLabel(this.chart.data.datasets[datasetIndex].data[index]);
	},

	//Utils
	getPixelForValue:function(value){
		varme=this;
		returnme.getPixelForDecimal((+me.getRightValue(value)-me._startValue)/me._valueRange);
	},

	getValueForPixel:function(pixel){
		returnthis._startValue+this.getDecimalForPixel(pixel)*this._valueRange;
	},

	getPixelForTick:function(index){
		varticks=this.ticksAsNumbers;
		if(index<0||index>ticks.length-1){
			returnnull;
		}
		returnthis.getPixelForValue(ticks[index]);
	}
});

//INTERNAL:staticdefaultoptions,registeredinsrc/index.js
var_defaults$1=defaultConfig$1;
scale_linear._defaults=_defaults$1;

varvalueOrDefault$b=helpers$1.valueOrDefault;
varlog10=helpers$1.math.log10;

/**
 *Generateasetoflogarithmicticks
 *@paramgenerationOptionstheoptionsusedtogeneratetheticks
 *@paramdataRangetherangeofthedata
 *@returns{number[]}arrayoftickvalues
 */
functiongenerateTicks$1(generationOptions,dataRange){
	varticks=[];

	vartickVal=valueOrDefault$b(generationOptions.min,Math.pow(10,Math.floor(log10(dataRange.min))));

	varendExp=Math.floor(log10(dataRange.max));
	varendSignificand=Math.ceil(dataRange.max/Math.pow(10,endExp));
	varexp,significand;

	if(tickVal===0){
		exp=Math.floor(log10(dataRange.minNotZero));
		significand=Math.floor(dataRange.minNotZero/Math.pow(10,exp));

		ticks.push(tickVal);
		tickVal=significand*Math.pow(10,exp);
	}else{
		exp=Math.floor(log10(tickVal));
		significand=Math.floor(tickVal/Math.pow(10,exp));
	}
	varprecision=exp<0?Math.pow(10,Math.abs(exp)):1;

	do{
		ticks.push(tickVal);

		++significand;
		if(significand===10){
			significand=1;
			++exp;
			precision=exp>=0?1:precision;
		}

		tickVal=Math.round(significand*Math.pow(10,exp)*precision)/precision;
	}while(exp<endExp||(exp===endExp&&significand<endSignificand));

	varlastTick=valueOrDefault$b(generationOptions.max,tickVal);
	ticks.push(lastTick);

	returnticks;
}

vardefaultConfig$2={
	position:'left',

	//labelsettings
	ticks:{
		callback:core_ticks.formatters.logarithmic
	}
};

//TODO(v3):changethistopositiveOrDefault
functionnonNegativeOrDefault(value,defaultValue){
	returnhelpers$1.isFinite(value)&&value>=0?value:defaultValue;
}

varscale_logarithmic=core_scale.extend({
	determineDataLimits:function(){
		varme=this;
		varopts=me.options;
		varchart=me.chart;
		vardatasets=chart.data.datasets;
		varisHorizontal=me.isHorizontal();
		functionIDMatches(meta){
			returnisHorizontal?meta.xAxisID===me.id:meta.yAxisID===me.id;
		}
		vardatasetIndex,meta,value,data,i,ilen;

		//CalculateRange
		me.min=Number.POSITIVE_INFINITY;
		me.max=Number.NEGATIVE_INFINITY;
		me.minNotZero=Number.POSITIVE_INFINITY;

		varhasStacks=opts.stacked;
		if(hasStacks===undefined){
			for(datasetIndex=0;datasetIndex<datasets.length;datasetIndex++){
				meta=chart.getDatasetMeta(datasetIndex);
				if(chart.isDatasetVisible(datasetIndex)&&IDMatches(meta)&&
					meta.stack!==undefined){
					hasStacks=true;
					break;
				}
			}
		}

		if(opts.stacked||hasStacks){
			varvaluesPerStack={};

			for(datasetIndex=0;datasetIndex<datasets.length;datasetIndex++){
				meta=chart.getDatasetMeta(datasetIndex);
				varkey=[
					meta.type,
					//wehaveaseparatestackforstack=undefineddatasetswhentheopts.stackedisundefined
					((opts.stacked===undefined&&meta.stack===undefined)?datasetIndex:''),
					meta.stack
				].join('.');

				if(chart.isDatasetVisible(datasetIndex)&&IDMatches(meta)){
					if(valuesPerStack[key]===undefined){
						valuesPerStack[key]=[];
					}

					data=datasets[datasetIndex].data;
					for(i=0,ilen=data.length;i<ilen;i++){
						varvalues=valuesPerStack[key];
						value=me._parseValue(data[i]);
						//invalid,hiddenandnegativevaluesareignored
						if(isNaN(value.min)||isNaN(value.max)||meta.data[i].hidden||value.min<0||value.max<0){
							continue;
						}
						values[i]=values[i]||0;
						values[i]+=value.max;
					}
				}
			}

			helpers$1.each(valuesPerStack,function(valuesForType){
				if(valuesForType.length>0){
					varminVal=helpers$1.min(valuesForType);
					varmaxVal=helpers$1.max(valuesForType);
					me.min=Math.min(me.min,minVal);
					me.max=Math.max(me.max,maxVal);
				}
			});

		}else{
			for(datasetIndex=0;datasetIndex<datasets.length;datasetIndex++){
				meta=chart.getDatasetMeta(datasetIndex);
				if(chart.isDatasetVisible(datasetIndex)&&IDMatches(meta)){
					data=datasets[datasetIndex].data;
					for(i=0,ilen=data.length;i<ilen;i++){
						value=me._parseValue(data[i]);
						//invalid,hiddenandnegativevaluesareignored
						if(isNaN(value.min)||isNaN(value.max)||meta.data[i].hidden||value.min<0||value.max<0){
							continue;
						}

						me.min=Math.min(value.min,me.min);
						me.max=Math.max(value.max,me.max);

						if(value.min!==0){
							me.minNotZero=Math.min(value.min,me.minNotZero);
						}
					}
				}
			}
		}

		me.min=helpers$1.isFinite(me.min)?me.min:null;
		me.max=helpers$1.isFinite(me.max)?me.max:null;
		me.minNotZero=helpers$1.isFinite(me.minNotZero)?me.minNotZero:null;

		//Commonbaseimplementationtohandleticks.min,ticks.max
		this.handleTickRangeOptions();
	},

	handleTickRangeOptions:function(){
		varme=this;
		vartickOpts=me.options.ticks;
		varDEFAULT_MIN=1;
		varDEFAULT_MAX=10;

		me.min=nonNegativeOrDefault(tickOpts.min,me.min);
		me.max=nonNegativeOrDefault(tickOpts.max,me.max);

		if(me.min===me.max){
			if(me.min!==0&&me.min!==null){
				me.min=Math.pow(10,Math.floor(log10(me.min))-1);
				me.max=Math.pow(10,Math.floor(log10(me.max))+1);
			}else{
				me.min=DEFAULT_MIN;
				me.max=DEFAULT_MAX;
			}
		}
		if(me.min===null){
			me.min=Math.pow(10,Math.floor(log10(me.max))-1);
		}
		if(me.max===null){
			me.max=me.min!==0
				?Math.pow(10,Math.floor(log10(me.min))+1)
				:DEFAULT_MAX;
		}
		if(me.minNotZero===null){
			if(me.min>0){
				me.minNotZero=me.min;
			}elseif(me.max<1){
				me.minNotZero=Math.pow(10,Math.floor(log10(me.max)));
			}else{
				me.minNotZero=DEFAULT_MIN;
			}
		}
	},

	buildTicks:function(){
		varme=this;
		vartickOpts=me.options.ticks;
		varreverse=!me.isHorizontal();

		vargenerationOptions={
			min:nonNegativeOrDefault(tickOpts.min),
			max:nonNegativeOrDefault(tickOpts.max)
		};
		varticks=me.ticks=generateTicks$1(generationOptions,me);

		//Atthispoint,weneedtoupdateourmaxandmingiventhetickvaluessincewehaveexpandedthe
		//rangeofthescale
		me.max=helpers$1.max(ticks);
		me.min=helpers$1.min(ticks);

		if(tickOpts.reverse){
			reverse=!reverse;
			me.start=me.max;
			me.end=me.min;
		}else{
			me.start=me.min;
			me.end=me.max;
		}
		if(reverse){
			ticks.reverse();
		}
	},

	convertTicksToLabels:function(){
		this.tickValues=this.ticks.slice();

		core_scale.prototype.convertTicksToLabels.call(this);
	},

	//Getthecorrecttooltiplabel
	getLabelForIndex:function(index,datasetIndex){
		returnthis._getScaleLabel(this.chart.data.datasets[datasetIndex].data[index]);
	},

	getPixelForTick:function(index){
		varticks=this.tickValues;
		if(index<0||index>ticks.length-1){
			returnnull;
		}
		returnthis.getPixelForValue(ticks[index]);
	},

	/**
	*Returnsthevalueofthefirsttick.
	*@param{number}value-Theminimumnotzerovalue.
	*@return{number}Thefirsttickvalue.
	*@private
	*/
	_getFirstTickValue:function(value){
		varexp=Math.floor(log10(value));
		varsignificand=Math.floor(value/Math.pow(10,exp));

		returnsignificand*Math.pow(10,exp);
	},

	_configure:function(){
		varme=this;
		varstart=me.min;
		varoffset=0;

		core_scale.prototype._configure.call(me);

		if(start===0){
			start=me._getFirstTickValue(me.minNotZero);
			offset=valueOrDefault$b(me.options.ticks.fontSize,core_defaults.global.defaultFontSize)/me._length;
		}

		me._startValue=log10(start);
		me._valueOffset=offset;
		me._valueRange=(log10(me.max)-log10(start))/(1-offset);
	},

	getPixelForValue:function(value){
		varme=this;
		vardecimal=0;

		value=+me.getRightValue(value);

		if(value>me.min&&value>0){
			decimal=(log10(value)-me._startValue)/me._valueRange+me._valueOffset;
		}
		returnme.getPixelForDecimal(decimal);
	},

	getValueForPixel:function(pixel){
		varme=this;
		vardecimal=me.getDecimalForPixel(pixel);
		returndecimal===0&&me.min===0
			?0
			:Math.pow(10,me._startValue+(decimal-me._valueOffset)*me._valueRange);
	}
});

//INTERNAL:staticdefaultoptions,registeredinsrc/index.js
var_defaults$2=defaultConfig$2;
scale_logarithmic._defaults=_defaults$2;

varvalueOrDefault$c=helpers$1.valueOrDefault;
varvalueAtIndexOrDefault$1=helpers$1.valueAtIndexOrDefault;
varresolve$4=helpers$1.options.resolve;

vardefaultConfig$3={
	display:true,

	//Boolean-Whethertoanimatescalingthechartfromthecentre
	animate:true,
	position:'chartArea',

	angleLines:{
		display:true,
		color:'rgba(0,0,0,0.1)',
		lineWidth:1,
		borderDash:[],
		borderDashOffset:0.0
	},

	gridLines:{
		circular:false
	},

	//labelsettings
	ticks:{
		//Boolean-Showabackdroptothescalelabel
		showLabelBackdrop:true,

		//String-Thecolourofthelabelbackdrop
		backdropColor:'rgba(255,255,255,0.75)',

		//Number-Thebackdroppaddingabove&belowthelabelinpixels
		backdropPaddingY:2,

		//Number-Thebackdroppaddingtothesideofthelabelinpixels
		backdropPaddingX:2,

		callback:core_ticks.formatters.linear
	},

	pointLabels:{
		//Boolean-iftrue,showpointlabels
		display:true,

		//Number-Pointlabelfontsizeinpixels
		fontSize:10,

		//Function-Usedtoconvertpointlabels
		callback:function(label){
			returnlabel;
		}
	}
};

functiongetTickBackdropHeight(opts){
	vartickOpts=opts.ticks;

	if(tickOpts.display&&opts.display){
		returnvalueOrDefault$c(tickOpts.fontSize,core_defaults.global.defaultFontSize)+tickOpts.backdropPaddingY*2;
	}
	return0;
}

functionmeasureLabelSize(ctx,lineHeight,label){
	if(helpers$1.isArray(label)){
		return{
			w:helpers$1.longestText(ctx,ctx.font,label),
			h:label.length*lineHeight
		};
	}

	return{
		w:ctx.measureText(label).width,
		h:lineHeight
	};
}

functiondetermineLimits(angle,pos,size,min,max){
	if(angle===min||angle===max){
		return{
			start:pos-(size/2),
			end:pos+(size/2)
		};
	}elseif(angle<min||angle>max){
		return{
			start:pos-size,
			end:pos
		};
	}

	return{
		start:pos,
		end:pos+size
	};
}

/**
 *Helperfunctiontofitaradiallinearscalewithpointlabels
 */
functionfitWithPointLabels(scale){

	//Right,thisisreallyconfusingandthereisalotofmathsgoingonhere
	//Thegistoftheproblemishere:https://gist.github.com/nnnick/696cc9c55f4b0beb8fe9
	//
	//Reaction:https://dl.dropboxusercontent.com/u/34601363/toomuchscience.gif
	//
	//Solution:
	//
	//Weassumetheradiusofthepolygonishalfthesizeofthecanvasatfirst
	//ateachindexwecheckifthetextoverlaps.
	//
	//Whereitdoes,westorethatangleandthatindex.
	//
	//Afterfindingthelargestindexandanglewecalculatehowmuchweneedtoremove
	//fromtheshaperadiustomovethepointinwardsbythatx.
	//
	//Weaveragetheleftandrightdistancestogetthemaximumshaperadiusthatcanfitinthebox
	//alongwithlabels.
	//
	//Oncewehavethat,wecanfindthecentrepointforthechart,bytakingthextextprotrusion
	//oneachside,removingthatfromthesize,halvingitandaddingtheleftxprotrusionwidth.
	//
	//Thiswillmeanwehaveashapefittedtothecanvas,aslargeasitcanbewiththelabels
	//andpositionitinthemostspaceefficientmanner
	//
	//https://dl.dropboxusercontent.com/u/34601363/yeahscience.gif

	varplFont=helpers$1.options._parseFont(scale.options.pointLabels);

	//Getmaximumradiusofthepolygon.Eitherhalftheheight(minusthetextwidth)orhalfthewidth.
	//Usethistocalculatetheoffset+change.-MakesureL/Rprotrusionisatleast0tostopissueswithcentrepoints
	varfurthestLimits={
		l:0,
		r:scale.width,
		t:0,
		b:scale.height-scale.paddingTop
	};
	varfurthestAngles={};
	vari,textSize,pointPosition;

	scale.ctx.font=plFont.string;
	scale._pointLabelSizes=[];

	varvalueCount=scale.chart.data.labels.length;
	for(i=0;i<valueCount;i++){
		pointPosition=scale.getPointPosition(i,scale.drawingArea+5);
		textSize=measureLabelSize(scale.ctx,plFont.lineHeight,scale.pointLabels[i]);
		scale._pointLabelSizes[i]=textSize;

		//Addquartercircletomakedegree0meantopofcircle
		varangleRadians=scale.getIndexAngle(i);
		varangle=helpers$1.toDegrees(angleRadians)%360;
		varhLimits=determineLimits(angle,pointPosition.x,textSize.w,0,180);
		varvLimits=determineLimits(angle,pointPosition.y,textSize.h,90,270);

		if(hLimits.start<furthestLimits.l){
			furthestLimits.l=hLimits.start;
			furthestAngles.l=angleRadians;
		}

		if(hLimits.end>furthestLimits.r){
			furthestLimits.r=hLimits.end;
			furthestAngles.r=angleRadians;
		}

		if(vLimits.start<furthestLimits.t){
			furthestLimits.t=vLimits.start;
			furthestAngles.t=angleRadians;
		}

		if(vLimits.end>furthestLimits.b){
			furthestLimits.b=vLimits.end;
			furthestAngles.b=angleRadians;
		}
	}

	scale.setReductions(scale.drawingArea,furthestLimits,furthestAngles);
}

functiongetTextAlignForAngle(angle){
	if(angle===0||angle===180){
		return'center';
	}elseif(angle<180){
		return'left';
	}

	return'right';
}

functionfillText(ctx,text,position,lineHeight){
	vary=position.y+lineHeight/2;
	vari,ilen;

	if(helpers$1.isArray(text)){
		for(i=0,ilen=text.length;i<ilen;++i){
			ctx.fillText(text[i],position.x,y);
			y+=lineHeight;
		}
	}else{
		ctx.fillText(text,position.x,y);
	}
}

functionadjustPointPositionForLabelHeight(angle,textSize,position){
	if(angle===90||angle===270){
		position.y-=(textSize.h/2);
	}elseif(angle>270||angle<90){
		position.y-=textSize.h;
	}
}

functiondrawPointLabels(scale){
	varctx=scale.ctx;
	varopts=scale.options;
	varpointLabelOpts=opts.pointLabels;
	vartickBackdropHeight=getTickBackdropHeight(opts);
	varouterDistance=scale.getDistanceFromCenterForValue(opts.ticks.reverse?scale.min:scale.max);
	varplFont=helpers$1.options._parseFont(pointLabelOpts);

	ctx.save();

	ctx.font=plFont.string;
	ctx.textBaseline='middle';

	for(vari=scale.chart.data.labels.length-1;i>=0;i--){
		//Extrapixelsoutforsomelabelspacing
		varextra=(i===0?tickBackdropHeight/2:0);
		varpointLabelPosition=scale.getPointPosition(i,outerDistance+extra+5);

		//Keepthisinloopsincewemaysupportarraypropertieshere
		varpointLabelFontColor=valueAtIndexOrDefault$1(pointLabelOpts.fontColor,i,core_defaults.global.defaultFontColor);
		ctx.fillStyle=pointLabelFontColor;

		varangleRadians=scale.getIndexAngle(i);
		varangle=helpers$1.toDegrees(angleRadians);
		ctx.textAlign=getTextAlignForAngle(angle);
		adjustPointPositionForLabelHeight(angle,scale._pointLabelSizes[i],pointLabelPosition);
		fillText(ctx,scale.pointLabels[i],pointLabelPosition,plFont.lineHeight);
	}
	ctx.restore();
}

functiondrawRadiusLine(scale,gridLineOpts,radius,index){
	varctx=scale.ctx;
	varcircular=gridLineOpts.circular;
	varvalueCount=scale.chart.data.labels.length;
	varlineColor=valueAtIndexOrDefault$1(gridLineOpts.color,index-1);
	varlineWidth=valueAtIndexOrDefault$1(gridLineOpts.lineWidth,index-1);
	varpointPosition;

	if((!circular&&!valueCount)||!lineColor||!lineWidth){
		return;
	}

	ctx.save();
	ctx.strokeStyle=lineColor;
	ctx.lineWidth=lineWidth;
	if(ctx.setLineDash){
		ctx.setLineDash(gridLineOpts.borderDash||[]);
		ctx.lineDashOffset=gridLineOpts.borderDashOffset||0.0;
	}

	ctx.beginPath();
	if(circular){
		//Drawcirculararcsbetweenthepoints
		ctx.arc(scale.xCenter,scale.yCenter,radius,0,Math.PI*2);
	}else{
		//Drawstraightlinesconnectingeachindex
		pointPosition=scale.getPointPosition(0,radius);
		ctx.moveTo(pointPosition.x,pointPosition.y);

		for(vari=1;i<valueCount;i++){
			pointPosition=scale.getPointPosition(i,radius);
			ctx.lineTo(pointPosition.x,pointPosition.y);
		}
	}
	ctx.closePath();
	ctx.stroke();
	ctx.restore();
}

functionnumberOrZero(param){
	returnhelpers$1.isNumber(param)?param:0;
}

varscale_radialLinear=scale_linearbase.extend({
	setDimensions:function(){
		varme=this;

		//Settheunconstraineddimensionbeforelabelrotation
		me.width=me.maxWidth;
		me.height=me.maxHeight;
		me.paddingTop=getTickBackdropHeight(me.options)/2;
		me.xCenter=Math.floor(me.width/2);
		me.yCenter=Math.floor((me.height-me.paddingTop)/2);
		me.drawingArea=Math.min(me.height-me.paddingTop,me.width)/2;
	},

	determineDataLimits:function(){
		varme=this;
		varchart=me.chart;
		varmin=Number.POSITIVE_INFINITY;
		varmax=Number.NEGATIVE_INFINITY;

		helpers$1.each(chart.data.datasets,function(dataset,datasetIndex){
			if(chart.isDatasetVisible(datasetIndex)){
				varmeta=chart.getDatasetMeta(datasetIndex);

				helpers$1.each(dataset.data,function(rawValue,index){
					varvalue=+me.getRightValue(rawValue);
					if(isNaN(value)||meta.data[index].hidden){
						return;
					}

					min=Math.min(value,min);
					max=Math.max(value,max);
				});
			}
		});

		me.min=(min===Number.POSITIVE_INFINITY?0:min);
		me.max=(max===Number.NEGATIVE_INFINITY?0:max);

		//Commonbaseimplementationtohandleticks.min,ticks.max,ticks.beginAtZero
		me.handleTickRangeOptions();
	},

	//Returnsthemaximumnumberofticksbasedonthescaledimension
	_computeTickLimit:function(){
		returnMath.ceil(this.drawingArea/getTickBackdropHeight(this.options));
	},

	convertTicksToLabels:function(){
		varme=this;

		scale_linearbase.prototype.convertTicksToLabels.call(me);

		//Pointlabels
		me.pointLabels=me.chart.data.labels.map(function(){
			varlabel=helpers$1.callback(me.options.pointLabels.callback,arguments,me);
			returnlabel||label===0?label:'';
		});
	},

	getLabelForIndex:function(index,datasetIndex){
		return+this.getRightValue(this.chart.data.datasets[datasetIndex].data[index]);
	},

	fit:function(){
		varme=this;
		varopts=me.options;

		if(opts.display&&opts.pointLabels.display){
			fitWithPointLabels(me);
		}else{
			me.setCenterPoint(0,0,0,0);
		}
	},

	/**
	*Setradiusreductionsanddeterminenewradiusandcenterpoint
	*@private
	*/
	setReductions:function(largestPossibleRadius,furthestLimits,furthestAngles){
		varme=this;
		varradiusReductionLeft=furthestLimits.l/Math.sin(furthestAngles.l);
		varradiusReductionRight=Math.max(furthestLimits.r-me.width,0)/Math.sin(furthestAngles.r);
		varradiusReductionTop=-furthestLimits.t/Math.cos(furthestAngles.t);
		varradiusReductionBottom=-Math.max(furthestLimits.b-(me.height-me.paddingTop),0)/Math.cos(furthestAngles.b);

		radiusReductionLeft=numberOrZero(radiusReductionLeft);
		radiusReductionRight=numberOrZero(radiusReductionRight);
		radiusReductionTop=numberOrZero(radiusReductionTop);
		radiusReductionBottom=numberOrZero(radiusReductionBottom);

		me.drawingArea=Math.min(
			Math.floor(largestPossibleRadius-(radiusReductionLeft+radiusReductionRight)/2),
			Math.floor(largestPossibleRadius-(radiusReductionTop+radiusReductionBottom)/2));
		me.setCenterPoint(radiusReductionLeft,radiusReductionRight,radiusReductionTop,radiusReductionBottom);
	},

	setCenterPoint:function(leftMovement,rightMovement,topMovement,bottomMovement){
		varme=this;
		varmaxRight=me.width-rightMovement-me.drawingArea;
		varmaxLeft=leftMovement+me.drawingArea;
		varmaxTop=topMovement+me.drawingArea;
		varmaxBottom=(me.height-me.paddingTop)-bottomMovement-me.drawingArea;

		me.xCenter=Math.floor(((maxLeft+maxRight)/2)+me.left);
		me.yCenter=Math.floor(((maxTop+maxBottom)/2)+me.top+me.paddingTop);
	},

	getIndexAngle:function(index){
		varchart=this.chart;
		varangleMultiplier=360/chart.data.labels.length;
		varoptions=chart.options||{};
		varstartAngle=options.startAngle||0;

		//Startfromthetopinsteadofright,soremoveaquarterofthecircle
		varangle=(index*angleMultiplier+startAngle)%360;

		return(angle<0?angle+360:angle)*Math.PI*2/360;
	},

	getDistanceFromCenterForValue:function(value){
		varme=this;

		if(helpers$1.isNullOrUndef(value)){
			returnNaN;
		}

		//Takeintoaccounthalffontsize+theyPaddingofthetopvalue
		varscalingFactor=me.drawingArea/(me.max-me.min);
		if(me.options.ticks.reverse){
			return(me.max-value)*scalingFactor;
		}
		return(value-me.min)*scalingFactor;
	},

	getPointPosition:function(index,distanceFromCenter){
		varme=this;
		varthisAngle=me.getIndexAngle(index)-(Math.PI/2);
		return{
			x:Math.cos(thisAngle)*distanceFromCenter+me.xCenter,
			y:Math.sin(thisAngle)*distanceFromCenter+me.yCenter
		};
	},

	getPointPositionForValue:function(index,value){
		returnthis.getPointPosition(index,this.getDistanceFromCenterForValue(value));
	},

	getBasePosition:function(index){
		varme=this;
		varmin=me.min;
		varmax=me.max;

		returnme.getPointPositionForValue(index||0,
			me.beginAtZero?0:
			min<0&&max<0?max:
			min>0&&max>0?min:
			0);
	},

	/**
	*@private
	*/
	_drawGrid:function(){
		varme=this;
		varctx=me.ctx;
		varopts=me.options;
		vargridLineOpts=opts.gridLines;
		varangleLineOpts=opts.angleLines;
		varlineWidth=valueOrDefault$c(angleLineOpts.lineWidth,gridLineOpts.lineWidth);
		varlineColor=valueOrDefault$c(angleLineOpts.color,gridLineOpts.color);
		vari,offset,position;

		if(opts.pointLabels.display){
			drawPointLabels(me);
		}

		if(gridLineOpts.display){
			helpers$1.each(me.ticks,function(label,index){
				if(index!==0){
					offset=me.getDistanceFromCenterForValue(me.ticksAsNumbers[index]);
					drawRadiusLine(me,gridLineOpts,offset,index);
				}
			});
		}

		if(angleLineOpts.display&&lineWidth&&lineColor){
			ctx.save();
			ctx.lineWidth=lineWidth;
			ctx.strokeStyle=lineColor;
			if(ctx.setLineDash){
				ctx.setLineDash(resolve$4([angleLineOpts.borderDash,gridLineOpts.borderDash,[]]));
				ctx.lineDashOffset=resolve$4([angleLineOpts.borderDashOffset,gridLineOpts.borderDashOffset,0.0]);
			}

			for(i=me.chart.data.labels.length-1;i>=0;i--){
				offset=me.getDistanceFromCenterForValue(opts.ticks.reverse?me.min:me.max);
				position=me.getPointPosition(i,offset);
				ctx.beginPath();
				ctx.moveTo(me.xCenter,me.yCenter);
				ctx.lineTo(position.x,position.y);
				ctx.stroke();
			}

			ctx.restore();
		}
	},

	/**
	*@private
	*/
	_drawLabels:function(){
		varme=this;
		varctx=me.ctx;
		varopts=me.options;
		vartickOpts=opts.ticks;

		if(!tickOpts.display){
			return;
		}

		varstartAngle=me.getIndexAngle(0);
		vartickFont=helpers$1.options._parseFont(tickOpts);
		vartickFontColor=valueOrDefault$c(tickOpts.fontColor,core_defaults.global.defaultFontColor);
		varoffset,width;

		ctx.save();
		ctx.font=tickFont.string;
		ctx.translate(me.xCenter,me.yCenter);
		ctx.rotate(startAngle);
		ctx.textAlign='center';
		ctx.textBaseline='middle';

		helpers$1.each(me.ticks,function(label,index){
			if(index===0&&!tickOpts.reverse){
				return;
			}

			offset=me.getDistanceFromCenterForValue(me.ticksAsNumbers[index]);

			if(tickOpts.showLabelBackdrop){
				width=ctx.measureText(label).width;
				ctx.fillStyle=tickOpts.backdropColor;

				ctx.fillRect(
					-width/2-tickOpts.backdropPaddingX,
					-offset-tickFont.size/2-tickOpts.backdropPaddingY,
					width+tickOpts.backdropPaddingX*2,
					tickFont.size+tickOpts.backdropPaddingY*2
				);
			}

			ctx.fillStyle=tickFontColor;
			ctx.fillText(label,0,-offset);
		});

		ctx.restore();
	},

	/**
	*@private
	*/
	_drawTitle:helpers$1.noop
});

//INTERNAL:staticdefaultoptions,registeredinsrc/index.js
var_defaults$3=defaultConfig$3;
scale_radialLinear._defaults=_defaults$3;

vardeprecated$1=helpers$1._deprecated;
varresolve$5=helpers$1.options.resolve;
varvalueOrDefault$d=helpers$1.valueOrDefault;

//IntegerconstantsarefromtheES6spec.
varMIN_INTEGER=Number.MIN_SAFE_INTEGER||-9007199254740991;
varMAX_INTEGER=Number.MAX_SAFE_INTEGER||9007199254740991;

varINTERVALS={
	millisecond:{
		common:true,
		size:1,
		steps:1000
	},
	second:{
		common:true,
		size:1000,
		steps:60
	},
	minute:{
		common:true,
		size:60000,
		steps:60
	},
	hour:{
		common:true,
		size:3600000,
		steps:24
	},
	day:{
		common:true,
		size:86400000,
		steps:30
	},
	week:{
		common:false,
		size:604800000,
		steps:4
	},
	month:{
		common:true,
		size:2.628e9,
		steps:12
	},
	quarter:{
		common:false,
		size:7.884e9,
		steps:4
	},
	year:{
		common:true,
		size:3.154e10
	}
};

varUNITS=Object.keys(INTERVALS);

functionsorter(a,b){
	returna-b;
}

functionarrayUnique(items){
	varhash={};
	varout=[];
	vari,ilen,item;

	for(i=0,ilen=items.length;i<ilen;++i){
		item=items[i];
		if(!hash[item]){
			hash[item]=true;
			out.push(item);
		}
	}

	returnout;
}

functiongetMin(options){
	returnhelpers$1.valueOrDefault(options.time.min,options.ticks.min);
}

functiongetMax(options){
	returnhelpers$1.valueOrDefault(options.time.max,options.ticks.max);
}

/**
 *Returnsanarrayof{time,pos}objectsusedtointerpolateaspecific`time`orposition
 *(`pos`)onthescale,bysearchingentriesbeforeandaftertherequestedvalue.`pos`is
 *adecimalbetween0and1:0beingthestartofthescale(leftortop)and1theother
 *extremity(left+widthortop+height).Notethatitwouldbemoreoptimizedtodirectly
 *storepre-computedpixels,butthescaledimensionsarenotguaranteedatthetimeweneed
 *tocreatethelookuptable.ThetableALWAYScontainsatleasttwoitems:minandmax.
 *
 *@param{number[]}timestamps-timestampssortedfromlowesttohighest.
 *@param{string}distribution-If'linear',timestampswillbespreadlinearlyalongthemin
 *andmaxrange,sobasically,thetablewillcontainsonlytwoitems:{min,0}and{max,1}.
 *If'series',timestampswillbepositionedatthesamedistancefromeachother.Inthis
 *case,onlytimestampsthatbreakthetimelinearityareregistered,meaningthatinthe
 *bestcase,alltimestampsarelinear,thetablecontainsonlyminandmax.
 */
functionbuildLookupTable(timestamps,min,max,distribution){
	if(distribution==='linear'||!timestamps.length){
		return[
			{time:min,pos:0},
			{time:max,pos:1}
		];
	}

	vartable=[];
	varitems=[min];
	vari,ilen,prev,curr,next;

	for(i=0,ilen=timestamps.length;i<ilen;++i){
		curr=timestamps[i];
		if(curr>min&&curr<max){
			items.push(curr);
		}
	}

	items.push(max);

	for(i=0,ilen=items.length;i<ilen;++i){
		next=items[i+1];
		prev=items[i-1];
		curr=items[i];

		//onlyaddpointsthatbreaksthescalelinearity
		if(prev===undefined||next===undefined||Math.round((next+prev)/2)!==curr){
			table.push({time:curr,pos:i/(ilen-1)});
		}
	}

	returntable;
}

//@seeadaptedfromhttps://www.anujgakhar.com/2014/03/01/binary-search-in-javascript/
functionlookup(table,key,value){
	varlo=0;
	varhi=table.length-1;
	varmid,i0,i1;

	while(lo>=0&&lo<=hi){
		mid=(lo+hi)>>1;
		i0=table[mid-1]||null;
		i1=table[mid];

		if(!i0){
			//givenvalueisoutsidetable(beforefirstitem)
			return{lo:null,hi:i1};
		}elseif(i1[key]<value){
			lo=mid+1;
		}elseif(i0[key]>value){
			hi=mid-1;
		}else{
			return{lo:i0,hi:i1};
		}
	}

	//givenvalueisoutsidetable(afterlastitem)
	return{lo:i1,hi:null};
}

/**
 *Linearlyinterpolatesthegivensource`value`usingthetableitems`skey`valuesand
 *returnstheassociated`tkey`value.Forexample,interpolate(table,'time',42,'pos')
 *returnsthepositionforatimestampequalto42.Ifvalueisoutofbounds,valuesat
 *index[0,1]or[n-1,n]areusedfortheinterpolation.
 */
functioninterpolate$1(table,skey,sval,tkey){
	varrange=lookup(table,skey,sval);

	//Note:thelookuptableALWAYScontainsatleast2items(minandmax)
	varprev=!range.lo?table[0]:!range.hi?table[table.length-2]:range.lo;
	varnext=!range.lo?table[1]:!range.hi?table[table.length-1]:range.hi;

	varspan=next[skey]-prev[skey];
	varratio=span?(sval-prev[skey])/span:0;
	varoffset=(next[tkey]-prev[tkey])*ratio;

	returnprev[tkey]+offset;
}

functiontoTimestamp(scale,input){
	varadapter=scale._adapter;
	varoptions=scale.options.time;
	varparser=options.parser;
	varformat=parser||options.format;
	varvalue=input;

	if(typeofparser==='function'){
		value=parser(value);
	}

	//Onlyparseifitsnotatimestampalready
	if(!helpers$1.isFinite(value)){
		value=typeofformat==='string'
			?adapter.parse(value,format)
			:adapter.parse(value);
	}

	if(value!==null){
		return+value;
	}

	//Labelsareinanincompatibleformatandno`parser`hasbeenprovided.
	//Theusermightstillusethedeprecated`format`optionforparsing.
	if(!parser&&typeofformat==='function'){
		value=format(input);

		//`format`couldreturnsomethingelsethanatimestamp,ifso,parseit
		if(!helpers$1.isFinite(value)){
			value=adapter.parse(value);
		}
	}

	returnvalue;
}

functionparse(scale,input){
	if(helpers$1.isNullOrUndef(input)){
		returnnull;
	}

	varoptions=scale.options.time;
	varvalue=toTimestamp(scale,scale.getRightValue(input));
	if(value===null){
		returnvalue;
	}

	if(options.round){
		value=+scale._adapter.startOf(value,options.round);
	}

	returnvalue;
}

/**
 *Figuresoutwhatunitresultsinanappropriatenumberofauto-generatedticks
 */
functiondetermineUnitForAutoTicks(minUnit,min,max,capacity){
	varilen=UNITS.length;
	vari,interval,factor;

	for(i=UNITS.indexOf(minUnit);i<ilen-1;++i){
		interval=INTERVALS[UNITS[i]];
		factor=interval.steps?interval.steps:MAX_INTEGER;

		if(interval.common&&Math.ceil((max-min)/(factor*interval.size))<=capacity){
			returnUNITS[i];
		}
	}

	returnUNITS[ilen-1];
}

/**
 *Figuresoutwhatunittoformatasetoftickswith
 */
functiondetermineUnitForFormatting(scale,numTicks,minUnit,min,max){
	vari,unit;

	for(i=UNITS.length-1;i>=UNITS.indexOf(minUnit);i--){
		unit=UNITS[i];
		if(INTERVALS[unit].common&&scale._adapter.diff(max,min,unit)>=numTicks-1){
			returnunit;
		}
	}

	returnUNITS[minUnit?UNITS.indexOf(minUnit):0];
}

functiondetermineMajorUnit(unit){
	for(vari=UNITS.indexOf(unit)+1,ilen=UNITS.length;i<ilen;++i){
		if(INTERVALS[UNITS[i]].common){
			returnUNITS[i];
		}
	}
}

/**
 *Generatesamaximumof`capacity`timestampsbetweenminandmax,roundedtothe
 *`minor`unitusingthegivenscaletime`options`.
 *Important:thismethodcanreturnticksoutsidetheminandmaxrange,it'sthe
 *responsibilityofthecallingcodetoclampvaluesifneeded.
 */
functiongenerate(scale,min,max,capacity){
	varadapter=scale._adapter;
	varoptions=scale.options;
	vartimeOpts=options.time;
	varminor=timeOpts.unit||determineUnitForAutoTicks(timeOpts.minUnit,min,max,capacity);
	varstepSize=resolve$5([timeOpts.stepSize,timeOpts.unitStepSize,1]);
	varweekday=minor==='week'?timeOpts.isoWeekday:false;
	varfirst=min;
	varticks=[];
	vartime;

	//For'week'unit,handlethefirstdayofweekoption
	if(weekday){
		first=+adapter.startOf(first,'isoWeek',weekday);
	}

	//Alignfirstticksonunit
	first=+adapter.startOf(first,weekday?'day':minor);

	//Preventbrowserfromfreezingincaseuseroptionsrequestmillionsofmilliseconds
	if(adapter.diff(max,min,minor)>100000*stepSize){
		throwmin+'and'+max+'aretoofarapartwithstepSizeof'+stepSize+''+minor;
	}

	for(time=first;time<max;time=+adapter.add(time,stepSize,minor)){
		ticks.push(time);
	}

	if(time===max||options.bounds==='ticks'){
		ticks.push(time);
	}

	returnticks;
}

/**
 *Returnsthestartandendoffsetsfromedgesintheformof{start,end}
 *whereeachvalueisarelativewidthtothescaleandrangesbetween0and1.
 *Theyaddextramarginsonthebothsidesbyscalingdowntheoriginalscale.
 *Offsetsareaddedwhenthe`offset`optionistrue.
 */
functioncomputeOffsets(table,ticks,min,max,options){
	varstart=0;
	varend=0;
	varfirst,last;

	if(options.offset&&ticks.length){
		first=interpolate$1(table,'time',ticks[0],'pos');
		if(ticks.length===1){
			start=1-first;
		}else{
			start=(interpolate$1(table,'time',ticks[1],'pos')-first)/2;
		}
		last=interpolate$1(table,'time',ticks[ticks.length-1],'pos');
		if(ticks.length===1){
			end=last;
		}else{
			end=(last-interpolate$1(table,'time',ticks[ticks.length-2],'pos'))/2;
		}
	}

	return{start:start,end:end,factor:1/(start+1+end)};
}

functionsetMajorTicks(scale,ticks,map,majorUnit){
	varadapter=scale._adapter;
	varfirst=+adapter.startOf(ticks[0].value,majorUnit);
	varlast=ticks[ticks.length-1].value;
	varmajor,index;

	for(major=first;major<=last;major=+adapter.add(major,1,majorUnit)){
		index=map[major];
		if(index>=0){
			ticks[index].major=true;
		}
	}
	returnticks;
}

functionticksFromTimestamps(scale,values,majorUnit){
	varticks=[];
	varmap={};
	varilen=values.length;
	vari,value;

	for(i=0;i<ilen;++i){
		value=values[i];
		map[value]=i;

		ticks.push({
			value:value,
			major:false
		});
	}

	//WesetthemajorticksseparatelyfromtheaboveloopbecausecallingstartOfforeverytick
	//isexpensivewhenthereisalargenumberofticks
	return(ilen===0||!majorUnit)?ticks:setMajorTicks(scale,ticks,map,majorUnit);
}

vardefaultConfig$4={
	position:'bottom',

	/**
	*Datadistributionalongthescale:
	*-'linear':dataarespreadaccordingtotheirtime(distancescanvary),
	*-'series':dataarespreadatthesamedistancefromeachother.
	*@seehttps://github.com/chartjs/Chart.js/pull/4507
	*@since2.7.0
	*/
	distribution:'linear',

	/**
	*Scaleboundarystrategy(bypassedbymin/maxtimeoptions)
	*-`data`:makesuredataarefullyvisible,ticksoutsideareremoved
	*-`ticks`:makesureticksarefullyvisible,dataoutsidearetruncated
	*@seehttps://github.com/chartjs/Chart.js/pull/4556
	*@since2.7.0
	*/
	bounds:'data',

	adapters:{},
	time:{
		parser:false,//false==apatternstringfromhttps://momentjs.com/docs/#/parsing/string-format/oracustomcallbackthatconvertsitsargumenttoamoment
		unit:false,//false==automaticoroverridewithweek,month,year,etc.
		round:false,//none,oroverridewithweek,month,year,etc.
		displayFormat:false,//DEPRECATED
		isoWeekday:false,//overrideweekstartday-seehttps://momentjs.com/docs/#/get-set/iso-weekday/
		minUnit:'millisecond',
		displayFormats:{}
	},
	ticks:{
		autoSkip:false,

		/**
		*Ticksgenerationinputvalues:
		*-'auto':generates"optimal"ticksbasedonscalesizeandtimeoptions.
		*-'data':generatesticksfromdata(includinglabelsfromdata{t|x|y}objects).
		*-'labels':generatesticksfromusergiven`data.labels`valuesONLY.
		*@seehttps://github.com/chartjs/Chart.js/pull/4507
		*@since2.7.0
		*/
		source:'auto',

		major:{
			enabled:false
		}
	}
};

varscale_time=core_scale.extend({
	initialize:function(){
		this.mergeTicksOptions();
		core_scale.prototype.initialize.call(this);
	},

	update:function(){
		varme=this;
		varoptions=me.options;
		vartime=options.time||(options.time={});
		varadapter=me._adapter=newcore_adapters._date(options.adapters.date);

		//DEPRECATIONS:outputamessageonlyonetimeperupdate
		deprecated$1('timescale',time.format,'time.format','time.parser');
		deprecated$1('timescale',time.min,'time.min','ticks.min');
		deprecated$1('timescale',time.max,'time.max','ticks.max');

		//Backwardcompatibility:beforeintroducingadapter,`displayFormats`was
		//supposedtocontain*all*unit/stringpairsbutthiscan'tberesolved
		//whenloadingthescale(adaptersareloadedafterward),solet'spopulate
		//missingformatsonupdate
		helpers$1.mergeIf(time.displayFormats,adapter.formats());

		returncore_scale.prototype.update.apply(me,arguments);
	},

	/**
	*Allowsdatatobereferencedvia't'attribute
	*/
	getRightValue:function(rawValue){
		if(rawValue&&rawValue.t!==undefined){
			rawValue=rawValue.t;
		}
		returncore_scale.prototype.getRightValue.call(this,rawValue);
	},

	determineDataLimits:function(){
		varme=this;
		varchart=me.chart;
		varadapter=me._adapter;
		varoptions=me.options;
		varunit=options.time.unit||'day';
		varmin=MAX_INTEGER;
		varmax=MIN_INTEGER;
		vartimestamps=[];
		vardatasets=[];
		varlabels=[];
		vari,j,ilen,jlen,data,timestamp,labelsAdded;
		vardataLabels=me._getLabels();

		for(i=0,ilen=dataLabels.length;i<ilen;++i){
			labels.push(parse(me,dataLabels[i]));
		}

		for(i=0,ilen=(chart.data.datasets||[]).length;i<ilen;++i){
			if(chart.isDatasetVisible(i)){
				data=chart.data.datasets[i].data;

				//Let'sconsiderthatalldatahavethesameformat.
				if(helpers$1.isObject(data[0])){
					datasets[i]=[];

					for(j=0,jlen=data.length;j<jlen;++j){
						timestamp=parse(me,data[j]);
						timestamps.push(timestamp);
						datasets[i][j]=timestamp;
					}
				}else{
					datasets[i]=labels.slice(0);
					if(!labelsAdded){
						timestamps=timestamps.concat(labels);
						labelsAdded=true;
					}
				}
			}else{
				datasets[i]=[];
			}
		}

		if(labels.length){
			min=Math.min(min,labels[0]);
			max=Math.max(max,labels[labels.length-1]);
		}

		if(timestamps.length){
			timestamps=ilen>1?arrayUnique(timestamps).sort(sorter):timestamps.sort(sorter);
			min=Math.min(min,timestamps[0]);
			max=Math.max(max,timestamps[timestamps.length-1]);
		}

		min=parse(me,getMin(options))||min;
		max=parse(me,getMax(options))||max;

		//Incasethereisnovalidmin/max,setlimitsbasedonunittimeoption
		min=min===MAX_INTEGER?+adapter.startOf(Date.now(),unit):min;
		max=max===MIN_INTEGER?+adapter.endOf(Date.now(),unit)+1:max;

		//Makesurethatmaxisstrictlyhigherthanmin(requiredbythelookuptable)
		me.min=Math.min(min,max);
		me.max=Math.max(min+1,max);

		//PRIVATE
		me._table=[];
		me._timestamps={
			data:timestamps,
			datasets:datasets,
			labels:labels
		};
	},

	buildTicks:function(){
		varme=this;
		varmin=me.min;
		varmax=me.max;
		varoptions=me.options;
		vartickOpts=options.ticks;
		vartimeOpts=options.time;
		vartimestamps=me._timestamps;
		varticks=[];
		varcapacity=me.getLabelCapacity(min);
		varsource=tickOpts.source;
		vardistribution=options.distribution;
		vari,ilen,timestamp;

		if(source==='data'||(source==='auto'&&distribution==='series')){
			timestamps=timestamps.data;
		}elseif(source==='labels'){
			timestamps=timestamps.labels;
		}else{
			timestamps=generate(me,min,max,capacity);
		}

		if(options.bounds==='ticks'&&timestamps.length){
			min=timestamps[0];
			max=timestamps[timestamps.length-1];
		}

		//Enforcelimitswithusermin/maxoptions
		min=parse(me,getMin(options))||min;
		max=parse(me,getMax(options))||max;

		//Removeticksoutsidethemin/maxrange
		for(i=0,ilen=timestamps.length;i<ilen;++i){
			timestamp=timestamps[i];
			if(timestamp>=min&&timestamp<=max){
				ticks.push(timestamp);
			}
		}

		me.min=min;
		me.max=max;

		//PRIVATE
		//determineUnitForFormattingreliesonthenumberoftickssowedon'tuseitwhen
		//autoSkipisenabledbecausewedon'tyetknowwhatthefinalnumberoftickswillbe
		me._unit=timeOpts.unit||(tickOpts.autoSkip
			?determineUnitForAutoTicks(timeOpts.minUnit,me.min,me.max,capacity)
			:determineUnitForFormatting(me,ticks.length,timeOpts.minUnit,me.min,me.max));
		me._majorUnit=!tickOpts.major.enabled||me._unit==='year'?undefined
			:determineMajorUnit(me._unit);
		me._table=buildLookupTable(me._timestamps.data,min,max,distribution);
		me._offsets=computeOffsets(me._table,ticks,min,max,options);

		if(tickOpts.reverse){
			ticks.reverse();
		}

		returnticksFromTimestamps(me,ticks,me._majorUnit);
	},

	getLabelForIndex:function(index,datasetIndex){
		varme=this;
		varadapter=me._adapter;
		vardata=me.chart.data;
		vartimeOpts=me.options.time;
		varlabel=data.labels&&index<data.labels.length?data.labels[index]:'';
		varvalue=data.datasets[datasetIndex].data[index];

		if(helpers$1.isObject(value)){
			label=me.getRightValue(value);
		}
		if(timeOpts.tooltipFormat){
			returnadapter.format(toTimestamp(me,label),timeOpts.tooltipFormat);
		}
		if(typeoflabel==='string'){
			returnlabel;
		}
		returnadapter.format(toTimestamp(me,label),timeOpts.displayFormats.datetime);
	},

	/**
	*Functiontoformatanindividualtickmark
	*@private
	*/
	tickFormatFunction:function(time,index,ticks,format){
		varme=this;
		varadapter=me._adapter;
		varoptions=me.options;
		varformats=options.time.displayFormats;
		varminorFormat=formats[me._unit];
		varmajorUnit=me._majorUnit;
		varmajorFormat=formats[majorUnit];
		vartick=ticks[index];
		vartickOpts=options.ticks;
		varmajor=majorUnit&&majorFormat&&tick&&tick.major;
		varlabel=adapter.format(time,format?format:major?majorFormat:minorFormat);
		varnestedTickOpts=major?tickOpts.major:tickOpts.minor;
		varformatter=resolve$5([
			nestedTickOpts.callback,
			nestedTickOpts.userCallback,
			tickOpts.callback,
			tickOpts.userCallback
		]);

		returnformatter?formatter(label,index,ticks):label;
	},

	convertTicksToLabels:function(ticks){
		varlabels=[];
		vari,ilen;

		for(i=0,ilen=ticks.length;i<ilen;++i){
			labels.push(this.tickFormatFunction(ticks[i].value,i,ticks));
		}

		returnlabels;
	},

	/**
	*@private
	*/
	getPixelForOffset:function(time){
		varme=this;
		varoffsets=me._offsets;
		varpos=interpolate$1(me._table,'time',time,'pos');
		returnme.getPixelForDecimal((offsets.start+pos)*offsets.factor);
	},

	getPixelForValue:function(value,index,datasetIndex){
		varme=this;
		vartime=null;

		if(index!==undefined&&datasetIndex!==undefined){
			time=me._timestamps.datasets[datasetIndex][index];
		}

		if(time===null){
			time=parse(me,value);
		}

		if(time!==null){
			returnme.getPixelForOffset(time);
		}
	},

	getPixelForTick:function(index){
		varticks=this.getTicks();
		returnindex>=0&&index<ticks.length?
			this.getPixelForOffset(ticks[index].value):
			null;
	},

	getValueForPixel:function(pixel){
		varme=this;
		varoffsets=me._offsets;
		varpos=me.getDecimalForPixel(pixel)/offsets.factor-offsets.end;
		vartime=interpolate$1(me._table,'pos',pos,'time');

		//DEPRECATION,weshouldreturntimedirectly
		returnme._adapter._create(time);
	},

	/**
	*@private
	*/
	_getLabelSize:function(label){
		varme=this;
		varticksOpts=me.options.ticks;
		vartickLabelWidth=me.ctx.measureText(label).width;
		varangle=helpers$1.toRadians(me.isHorizontal()?ticksOpts.maxRotation:ticksOpts.minRotation);
		varcosRotation=Math.cos(angle);
		varsinRotation=Math.sin(angle);
		vartickFontSize=valueOrDefault$d(ticksOpts.fontSize,core_defaults.global.defaultFontSize);

		return{
			w:(tickLabelWidth*cosRotation)+(tickFontSize*sinRotation),
			h:(tickLabelWidth*sinRotation)+(tickFontSize*cosRotation)
		};
	},

	/**
	*Crudeapproximationofwhatthelabelwidthmightbe
	*@private
	*/
	getLabelWidth:function(label){
		returnthis._getLabelSize(label).w;
	},

	/**
	*@private
	*/
	getLabelCapacity:function(exampleTime){
		varme=this;
		vartimeOpts=me.options.time;
		vardisplayFormats=timeOpts.displayFormats;

		//pickthelongestformat(milliseconds)forguestimation
		varformat=displayFormats[timeOpts.unit]||displayFormats.millisecond;
		varexampleLabel=me.tickFormatFunction(exampleTime,0,ticksFromTimestamps(me,[exampleTime],me._majorUnit),format);
		varsize=me._getLabelSize(exampleLabel);
		varcapacity=Math.floor(me.isHorizontal()?me.width/size.w:me.height/size.h);

		if(me.options.offset){
			capacity--;
		}

		returncapacity>0?capacity:1;
	}
});

//INTERNAL:staticdefaultoptions,registeredinsrc/index.js
var_defaults$4=defaultConfig$4;
scale_time._defaults=_defaults$4;

varscales={
	category:scale_category,
	linear:scale_linear,
	logarithmic:scale_logarithmic,
	radialLinear:scale_radialLinear,
	time:scale_time
};

varFORMATS={
	datetime:'MMMD,YYYY,h:mm:ssa',
	millisecond:'h:mm:ss.SSSa',
	second:'h:mm:ssa',
	minute:'h:mma',
	hour:'hA',
	day:'MMMD',
	week:'ll',
	month:'MMMYYYY',
	quarter:'[Q]Q-YYYY',
	year:'YYYY'
};

core_adapters._date.override(typeofmoment==='function'?{
	_id:'moment',//DEBUGONLY

	formats:function(){
		returnFORMATS;
	},

	parse:function(value,format){
		if(typeofvalue==='string'&&typeofformat==='string'){
			value=moment(value,format);
		}elseif(!(valueinstanceofmoment)){
			value=moment(value);
		}
		returnvalue.isValid()?value.valueOf():null;
	},

	format:function(time,format){
		returnmoment(time).format(format);
	},

	add:function(time,amount,unit){
		returnmoment(time).add(amount,unit).valueOf();
	},

	diff:function(max,min,unit){
		returnmoment(max).diff(moment(min),unit);
	},

	startOf:function(time,unit,weekday){
		time=moment(time);
		if(unit==='isoWeek'){
			returntime.isoWeekday(weekday).valueOf();
		}
		returntime.startOf(unit).valueOf();
	},

	endOf:function(time,unit){
		returnmoment(time).endOf(unit).valueOf();
	},

	//DEPRECATIONS

	/**
	*Providedforbackwardcompatibilitywithscale.getValueForPixel().
	*@deprecatedsinceversion2.8.0
	*@todoremoveatversion3
	*@private
	*/
	_create:function(time){
		returnmoment(time);
	},
}:{});

core_defaults._set('global',{
	plugins:{
		filler:{
			propagate:true
		}
	}
});

varmappers={
	dataset:function(source){
		varindex=source.fill;
		varchart=source.chart;
		varmeta=chart.getDatasetMeta(index);
		varvisible=meta&&chart.isDatasetVisible(index);
		varpoints=(visible&&meta.dataset._children)||[];
		varlength=points.length||0;

		return!length?null:function(point,i){
			return(i<length&&points[i]._view)||null;
		};
	},

	boundary:function(source){
		varboundary=source.boundary;
		varx=boundary?boundary.x:null;
		vary=boundary?boundary.y:null;

		if(helpers$1.isArray(boundary)){
			returnfunction(point,i){
				returnboundary[i];
			};
		}

		returnfunction(point){
			return{
				x:x===null?point.x:x,
				y:y===null?point.y:y,
			};
		};
	}
};

//@todoif(fill[0]==='#')
functiondecodeFill(el,index,count){
	varmodel=el._model||{};
	varfill=model.fill;
	vartarget;

	if(fill===undefined){
		fill=!!model.backgroundColor;
	}

	if(fill===false||fill===null){
		returnfalse;
	}

	if(fill===true){
		return'origin';
	}

	target=parseFloat(fill,10);
	if(isFinite(target)&&Math.floor(target)===target){
		if(fill[0]==='-'||fill[0]==='+'){
			target=index+target;
		}

		if(target===index||target<0||target>=count){
			returnfalse;
		}

		returntarget;
	}

	switch(fill){
	//compatibility
	case'bottom':
		return'start';
	case'top':
		return'end';
	case'zero':
		return'origin';
	//supportedboundaries
	case'origin':
	case'start':
	case'end':
		returnfill;
	//invalidfillvalues
	default:
		returnfalse;
	}
}

functioncomputeLinearBoundary(source){
	varmodel=source.el._model||{};
	varscale=source.el._scale||{};
	varfill=source.fill;
	vartarget=null;
	varhorizontal;

	if(isFinite(fill)){
		returnnull;
	}

	//Backwardcompatibility:untilv3,westillneedtosupportboundaryvaluesseton
	//themodel(scaleTop,scaleBottomandscaleZero)becausesomeexternalpluginsand
	//controllersmightstilluseit(e.g.theSmithchart).

	if(fill==='start'){
		target=model.scaleBottom===undefined?scale.bottom:model.scaleBottom;
	}elseif(fill==='end'){
		target=model.scaleTop===undefined?scale.top:model.scaleTop;
	}elseif(model.scaleZero!==undefined){
		target=model.scaleZero;
	}elseif(scale.getBasePixel){
		target=scale.getBasePixel();
	}

	if(target!==undefined&&target!==null){
		if(target.x!==undefined&&target.y!==undefined){
			returntarget;
		}

		if(helpers$1.isFinite(target)){
			horizontal=scale.isHorizontal();
			return{
				x:horizontal?target:null,
				y:horizontal?null:target
			};
		}
	}

	returnnull;
}

functioncomputeCircularBoundary(source){
	varscale=source.el._scale;
	varoptions=scale.options;
	varlength=scale.chart.data.labels.length;
	varfill=source.fill;
	vartarget=[];
	varstart,end,center,i,point;

	if(!length){
		returnnull;
	}

	start=options.ticks.reverse?scale.max:scale.min;
	end=options.ticks.reverse?scale.min:scale.max;
	center=scale.getPointPositionForValue(0,start);
	for(i=0;i<length;++i){
		point=fill==='start'||fill==='end'
			?scale.getPointPositionForValue(i,fill==='start'?start:end)
			:scale.getBasePosition(i);
		if(options.gridLines.circular){
			point.cx=center.x;
			point.cy=center.y;
			point.angle=scale.getIndexAngle(i)-Math.PI/2;
		}
		target.push(point);
	}
	returntarget;
}

functioncomputeBoundary(source){
	varscale=source.el._scale||{};

	if(scale.getPointPositionForValue){
		returncomputeCircularBoundary(source);
	}
	returncomputeLinearBoundary(source);
}

functionresolveTarget(sources,index,propagate){
	varsource=sources[index];
	varfill=source.fill;
	varvisited=[index];
	vartarget;

	if(!propagate){
		returnfill;
	}

	while(fill!==false&&visited.indexOf(fill)===-1){
		if(!isFinite(fill)){
			returnfill;
		}

		target=sources[fill];
		if(!target){
			returnfalse;
		}

		if(target.visible){
			returnfill;
		}

		visited.push(fill);
		fill=target.fill;
	}

	returnfalse;
}

functioncreateMapper(source){
	varfill=source.fill;
	vartype='dataset';

	if(fill===false){
		returnnull;
	}

	if(!isFinite(fill)){
		type='boundary';
	}

	returnmappers[type](source);
}

functionisDrawable(point){
	returnpoint&&!point.skip;
}

functiondrawArea(ctx,curve0,curve1,len0,len1){
	vari,cx,cy,r;

	if(!len0||!len1){
		return;
	}

	//buildingfirstareacurve(normal)
	ctx.moveTo(curve0[0].x,curve0[0].y);
	for(i=1;i<len0;++i){
		helpers$1.canvas.lineTo(ctx,curve0[i-1],curve0[i]);
	}

	if(curve1[0].angle!==undefined){
		cx=curve1[0].cx;
		cy=curve1[0].cy;
		r=Math.sqrt(Math.pow(curve1[0].x-cx,2)+Math.pow(curve1[0].y-cy,2));
		for(i=len1-1;i>0;--i){
			ctx.arc(cx,cy,r,curve1[i].angle,curve1[i-1].angle,true);
		}
		return;
	}

	//joiningthetwoareacurves
	ctx.lineTo(curve1[len1-1].x,curve1[len1-1].y);

	//buildingoppositeareacurve(reverse)
	for(i=len1-1;i>0;--i){
		helpers$1.canvas.lineTo(ctx,curve1[i],curve1[i-1],true);
	}
}

functiondoFill(ctx,points,mapper,view,color,loop){
	varcount=points.length;
	varspan=view.spanGaps;
	varcurve0=[];
	varcurve1=[];
	varlen0=0;
	varlen1=0;
	vari,ilen,index,p0,p1,d0,d1,loopOffset;

	ctx.beginPath();

	for(i=0,ilen=count;i<ilen;++i){
		index=i%count;
		p0=points[index]._view;
		p1=mapper(p0,index,view);
		d0=isDrawable(p0);
		d1=isDrawable(p1);

		if(loop&&loopOffset===undefined&&d0){
			loopOffset=i+1;
			ilen=count+loopOffset;
		}

		if(d0&&d1){
			len0=curve0.push(p0);
			len1=curve1.push(p1);
		}elseif(len0&&len1){
			if(!span){
				drawArea(ctx,curve0,curve1,len0,len1);
				len0=len1=0;
				curve0=[];
				curve1=[];
			}else{
				if(d0){
					curve0.push(p0);
				}
				if(d1){
					curve1.push(p1);
				}
			}
		}
	}

	drawArea(ctx,curve0,curve1,len0,len1);

	ctx.closePath();
	ctx.fillStyle=color;
	ctx.fill();
}

varplugin_filler={
	id:'filler',

	afterDatasetsUpdate:function(chart,options){
		varcount=(chart.data.datasets||[]).length;
		varpropagate=options.propagate;
		varsources=[];
		varmeta,i,el,source;

		for(i=0;i<count;++i){
			meta=chart.getDatasetMeta(i);
			el=meta.dataset;
			source=null;

			if(el&&el._model&&elinstanceofelements.Line){
				source={
					visible:chart.isDatasetVisible(i),
					fill:decodeFill(el,i,count),
					chart:chart,
					el:el
				};
			}

			meta.$filler=source;
			sources.push(source);
		}

		for(i=0;i<count;++i){
			source=sources[i];
			if(!source){
				continue;
			}

			source.fill=resolveTarget(sources,i,propagate);
			source.boundary=computeBoundary(source);
			source.mapper=createMapper(source);
		}
	},

	beforeDatasetsDraw:function(chart){
		varmetasets=chart._getSortedVisibleDatasetMetas();
		varctx=chart.ctx;
		varmeta,i,el,view,points,mapper,color;

		for(i=metasets.length-1;i>=0;--i){
			meta=metasets[i].$filler;

			if(!meta||!meta.visible){
				continue;
			}

			el=meta.el;
			view=el._view;
			points=el._children||[];
			mapper=meta.mapper;
			color=view.backgroundColor||core_defaults.global.defaultColor;

			if(mapper&&color&&points.length){
				helpers$1.canvas.clipArea(ctx,chart.chartArea);
				doFill(ctx,points,mapper,view,color,el._loop);
				helpers$1.canvas.unclipArea(ctx);
			}
		}
	}
};

vargetRtlHelper$1=helpers$1.rtl.getRtlAdapter;
varnoop$1=helpers$1.noop;
varvalueOrDefault$e=helpers$1.valueOrDefault;

core_defaults._set('global',{
	legend:{
		display:true,
		position:'top',
		align:'center',
		fullWidth:true,
		reverse:false,
		weight:1000,

		//acallbackthatwillhandle
		onClick:function(e,legendItem){
			varindex=legendItem.datasetIndex;
			varci=this.chart;
			varmeta=ci.getDatasetMeta(index);

			//Seecontroller.isDatasetVisiblecomment
			meta.hidden=meta.hidden===null?!ci.data.datasets[index].hidden:null;

			//Wehidadataset...rerenderthechart
			ci.update();
		},

		onHover:null,
		onLeave:null,

		labels:{
			boxWidth:40,
			padding:10,
			//Generateslabelsshowninthelegend
			//Validpropertiestoreturn:
			//text:texttodisplay
			//fillStyle:fillofcolouredbox
			//strokeStyle:strokeofcolouredbox
			//hidden:ifthislegenditemreferstoahiddenitem
			//lineCap:capstyleforline
			//lineDash
			//lineDashOffset:
			//lineJoin:
			//lineWidth:
			generateLabels:function(chart){
				vardatasets=chart.data.datasets;
				varoptions=chart.options.legend||{};
				varusePointStyle=options.labels&&options.labels.usePointStyle;

				returnchart._getSortedDatasetMetas().map(function(meta){
					varstyle=meta.controller.getStyle(usePointStyle?0:undefined);

					return{
						text:datasets[meta.index].label,
						fillStyle:style.backgroundColor,
						hidden:!chart.isDatasetVisible(meta.index),
						lineCap:style.borderCapStyle,
						lineDash:style.borderDash,
						lineDashOffset:style.borderDashOffset,
						lineJoin:style.borderJoinStyle,
						lineWidth:style.borderWidth,
						strokeStyle:style.borderColor,
						pointStyle:style.pointStyle,
						rotation:style.rotation,

						//Belowisextradatausedfortogglingthedatasets
						datasetIndex:meta.index
					};
				},this);
			}
		}
	},

	legendCallback:function(chart){
		varlist=document.createElement('ul');
		vardatasets=chart.data.datasets;
		vari,ilen,listItem,listItemSpan;

		list.setAttribute('class',chart.id+'-legend');

		for(i=0,ilen=datasets.length;i<ilen;i++){
			listItem=list.appendChild(document.createElement('li'));
			listItemSpan=listItem.appendChild(document.createElement('span'));
			listItemSpan.style.backgroundColor=datasets[i].backgroundColor;
			if(datasets[i].label){
				listItem.appendChild(document.createTextNode(datasets[i].label));
			}
		}

		returnlist.outerHTML;
	}
});

/**
 *HelperfunctiontogettheboxwidthbasedontheusePointStyleoption
 *@param{object}labelopts-thelabeloptionsonthelegend
 *@param{number}fontSize-thelabelfontsize
 *@return{number}widthofthecolorboxarea
 */
functiongetBoxWidth(labelOpts,fontSize){
	returnlabelOpts.usePointStyle&&labelOpts.boxWidth>fontSize?
		fontSize:
		labelOpts.boxWidth;
}

/**
 *IMPORTANT:thisclassisexposedpubliclyasChart.Legend,backwardcompatibilityrequired!
 */
varLegend=core_element.extend({

	initialize:function(config){
		varme=this;
		helpers$1.extend(me,config);

		//Containshitboxesforeachdataset(indatasetorder)
		me.legendHitBoxes=[];

		/**
 		*@private
 		*/
		me._hoveredItem=null;

		//Areweindoughnutmodewhichhasadifferentdatatype
		me.doughnutMode=false;
	},

	//Thesemethodsareorderedbylifecycle.Utilitiesthenfollow.
	//Anyfunctiondefinedhereisinheritedbyalllegendtypes.
	//Anyfunctioncanbeextendedbythelegendtype

	beforeUpdate:noop$1,
	update:function(maxWidth,maxHeight,margins){
		varme=this;

		//UpdateLifecycle-Probablydon'twanttoeverextendoroverwritethisfunction;)
		me.beforeUpdate();

		//Absorbthemastermeasurements
		me.maxWidth=maxWidth;
		me.maxHeight=maxHeight;
		me.margins=margins;

		//Dimensions
		me.beforeSetDimensions();
		me.setDimensions();
		me.afterSetDimensions();
		//Labels
		me.beforeBuildLabels();
		me.buildLabels();
		me.afterBuildLabels();

		//Fit
		me.beforeFit();
		me.fit();
		me.afterFit();
		//
		me.afterUpdate();

		returnme.minSize;
	},
	afterUpdate:noop$1,

	//

	beforeSetDimensions:noop$1,
	setDimensions:function(){
		varme=this;
		//Settheunconstraineddimensionbeforelabelrotation
		if(me.isHorizontal()){
			//Resetpositionbeforecalculatingrotation
			me.width=me.maxWidth;
			me.left=0;
			me.right=me.width;
		}else{
			me.height=me.maxHeight;

			//Resetpositionbeforecalculatingrotation
			me.top=0;
			me.bottom=me.height;
		}

		//Resetpadding
		me.paddingLeft=0;
		me.paddingTop=0;
		me.paddingRight=0;
		me.paddingBottom=0;

		//ResetminSize
		me.minSize={
			width:0,
			height:0
		};
	},
	afterSetDimensions:noop$1,

	//

	beforeBuildLabels:noop$1,
	buildLabels:function(){
		varme=this;
		varlabelOpts=me.options.labels||{};
		varlegendItems=helpers$1.callback(labelOpts.generateLabels,[me.chart],me)||[];

		if(labelOpts.filter){
			legendItems=legendItems.filter(function(item){
				returnlabelOpts.filter(item,me.chart.data);
			});
		}

		if(me.options.reverse){
			legendItems.reverse();
		}

		me.legendItems=legendItems;
	},
	afterBuildLabels:noop$1,

	//

	beforeFit:noop$1,
	fit:function(){
		varme=this;
		varopts=me.options;
		varlabelOpts=opts.labels;
		vardisplay=opts.display;

		varctx=me.ctx;

		varlabelFont=helpers$1.options._parseFont(labelOpts);
		varfontSize=labelFont.size;

		//Resethitboxes
		varhitboxes=me.legendHitBoxes=[];

		varminSize=me.minSize;
		varisHorizontal=me.isHorizontal();

		if(isHorizontal){
			minSize.width=me.maxWidth;//fillallthewidth
			minSize.height=display?10:0;
		}else{
			minSize.width=display?10:0;
			minSize.height=me.maxHeight;//fillalltheheight
		}

		//Increasesizeshere
		if(!display){
			me.width=minSize.width=me.height=minSize.height=0;
			return;
		}
		ctx.font=labelFont.string;

		if(isHorizontal){
			//Labels

			//Widthofeachlineoflegendboxes.Labelswrapontomultiplelineswhentherearetoomanytofitonone
			varlineWidths=me.lineWidths=[0];
			vartotalHeight=0;

			ctx.textAlign='left';
			ctx.textBaseline='middle';

			helpers$1.each(me.legendItems,function(legendItem,i){
				varboxWidth=getBoxWidth(labelOpts,fontSize);
				varwidth=boxWidth+(fontSize/2)+ctx.measureText(legendItem.text).width;

				if(i===0||lineWidths[lineWidths.length-1]+width+2*labelOpts.padding>minSize.width){
					totalHeight+=fontSize+labelOpts.padding;
					lineWidths[lineWidths.length-(i>0?0:1)]=0;
				}

				//Storethehitboxwidthandheighthere.Finalpositionwillbeupdatedin`draw`
				hitboxes[i]={
					left:0,
					top:0,
					width:width,
					height:fontSize
				};

				lineWidths[lineWidths.length-1]+=width+labelOpts.padding;
			});

			minSize.height+=totalHeight;

		}else{
			varvPadding=labelOpts.padding;
			varcolumnWidths=me.columnWidths=[];
			varcolumnHeights=me.columnHeights=[];
			vartotalWidth=labelOpts.padding;
			varcurrentColWidth=0;
			varcurrentColHeight=0;

			helpers$1.each(me.legendItems,function(legendItem,i){
				varboxWidth=getBoxWidth(labelOpts,fontSize);
				varitemWidth=boxWidth+(fontSize/2)+ctx.measureText(legendItem.text).width;

				//Iftootall,gotonewcolumn
				if(i>0&&currentColHeight+fontSize+2*vPadding>minSize.height){
					totalWidth+=currentColWidth+labelOpts.padding;
					columnWidths.push(currentColWidth);//previouscolumnwidth
					columnHeights.push(currentColHeight);
					currentColWidth=0;
					currentColHeight=0;
				}

				//Getmaxwidth
				currentColWidth=Math.max(currentColWidth,itemWidth);
				currentColHeight+=fontSize+vPadding;

				//Storethehitboxwidthandheighthere.Finalpositionwillbeupdatedin`draw`
				hitboxes[i]={
					left:0,
					top:0,
					width:itemWidth,
					height:fontSize
				};
			});

			totalWidth+=currentColWidth;
			columnWidths.push(currentColWidth);
			columnHeights.push(currentColHeight);
			minSize.width+=totalWidth;
		}

		me.width=minSize.width;
		me.height=minSize.height;
	},
	afterFit:noop$1,

	//SharedMethods
	isHorizontal:function(){
		returnthis.options.position==='top'||this.options.position==='bottom';
	},

	//Actuallydrawthelegendonthecanvas
	draw:function(){
		varme=this;
		varopts=me.options;
		varlabelOpts=opts.labels;
		varglobalDefaults=core_defaults.global;
		vardefaultColor=globalDefaults.defaultColor;
		varlineDefault=globalDefaults.elements.line;
		varlegendHeight=me.height;
		varcolumnHeights=me.columnHeights;
		varlegendWidth=me.width;
		varlineWidths=me.lineWidths;

		if(!opts.display){
			return;
		}

		varrtlHelper=getRtlHelper$1(opts.rtl,me.left,me.minSize.width);
		varctx=me.ctx;
		varfontColor=valueOrDefault$e(labelOpts.fontColor,globalDefaults.defaultFontColor);
		varlabelFont=helpers$1.options._parseFont(labelOpts);
		varfontSize=labelFont.size;
		varcursor;

		//Canvassetup
		ctx.textAlign=rtlHelper.textAlign('left');
		ctx.textBaseline='middle';
		ctx.lineWidth=0.5;
		ctx.strokeStyle=fontColor;//forstrikethrougheffect
		ctx.fillStyle=fontColor;//renderincorrectcolour
		ctx.font=labelFont.string;

		varboxWidth=getBoxWidth(labelOpts,fontSize);
		varhitboxes=me.legendHitBoxes;

		//currentposition
		vardrawLegendBox=function(x,y,legendItem){
			if(isNaN(boxWidth)||boxWidth<=0){
				return;
			}

			//Setthectxforthebox
			ctx.save();

			varlineWidth=valueOrDefault$e(legendItem.lineWidth,lineDefault.borderWidth);
			ctx.fillStyle=valueOrDefault$e(legendItem.fillStyle,defaultColor);
			ctx.lineCap=valueOrDefault$e(legendItem.lineCap,lineDefault.borderCapStyle);
			ctx.lineDashOffset=valueOrDefault$e(legendItem.lineDashOffset,lineDefault.borderDashOffset);
			ctx.lineJoin=valueOrDefault$e(legendItem.lineJoin,lineDefault.borderJoinStyle);
			ctx.lineWidth=lineWidth;
			ctx.strokeStyle=valueOrDefault$e(legendItem.strokeStyle,defaultColor);

			if(ctx.setLineDash){
				//IE9and10donotsupportlinedash
				ctx.setLineDash(valueOrDefault$e(legendItem.lineDash,lineDefault.borderDash));
			}

			if(labelOpts&&labelOpts.usePointStyle){
				//RecalculatexandyfordrawPoint()becauseitsexpecting
				//xandytobecenteroffigure(insteadoftopleft)
				varradius=boxWidth*Math.SQRT2/2;
				varcenterX=rtlHelper.xPlus(x,boxWidth/2);
				varcenterY=y+fontSize/2;

				//DrawpointStyleaslegendsymbol
				helpers$1.canvas.drawPoint(ctx,legendItem.pointStyle,radius,centerX,centerY,legendItem.rotation);
			}else{
				//Drawboxaslegendsymbol
				ctx.fillRect(rtlHelper.leftForLtr(x,boxWidth),y,boxWidth,fontSize);
				if(lineWidth!==0){
					ctx.strokeRect(rtlHelper.leftForLtr(x,boxWidth),y,boxWidth,fontSize);
				}
			}

			ctx.restore();
		};

		varfillText=function(x,y,legendItem,textWidth){
			varhalfFontSize=fontSize/2;
			varxLeft=rtlHelper.xPlus(x,boxWidth+halfFontSize);
			varyMiddle=y+halfFontSize;

			ctx.fillText(legendItem.text,xLeft,yMiddle);

			if(legendItem.hidden){
				//Strikethroughthetextifhidden
				ctx.beginPath();
				ctx.lineWidth=2;
				ctx.moveTo(xLeft,yMiddle);
				ctx.lineTo(rtlHelper.xPlus(xLeft,textWidth),yMiddle);
				ctx.stroke();
			}
		};

		varalignmentOffset=function(dimension,blockSize){
			switch(opts.align){
			case'start':
				returnlabelOpts.padding;
			case'end':
				returndimension-blockSize;
			default://center
				return(dimension-blockSize+labelOpts.padding)/2;
			}
		};

		//Horizontal
		varisHorizontal=me.isHorizontal();
		if(isHorizontal){
			cursor={
				x:me.left+alignmentOffset(legendWidth,lineWidths[0]),
				y:me.top+labelOpts.padding,
				line:0
			};
		}else{
			cursor={
				x:me.left+labelOpts.padding,
				y:me.top+alignmentOffset(legendHeight,columnHeights[0]),
				line:0
			};
		}

		helpers$1.rtl.overrideTextDirection(me.ctx,opts.textDirection);

		varitemHeight=fontSize+labelOpts.padding;
		helpers$1.each(me.legendItems,function(legendItem,i){
			vartextWidth=ctx.measureText(legendItem.text).width;
			varwidth=boxWidth+(fontSize/2)+textWidth;
			varx=cursor.x;
			vary=cursor.y;

			rtlHelper.setWidth(me.minSize.width);

			//Use(me.left+me.minSize.width)and(me.top+me.minSize.height)
			//insteadofme.rightandme.bottombecauseme.widthandme.height
			//mayhavebeenchangedsinceme.minSizewascalculated
			if(isHorizontal){
				if(i>0&&x+width+labelOpts.padding>me.left+me.minSize.width){
					y=cursor.y+=itemHeight;
					cursor.line++;
					x=cursor.x=me.left+alignmentOffset(legendWidth,lineWidths[cursor.line]);
				}
			}elseif(i>0&&y+itemHeight>me.top+me.minSize.height){
				x=cursor.x=x+me.columnWidths[cursor.line]+labelOpts.padding;
				cursor.line++;
				y=cursor.y=me.top+alignmentOffset(legendHeight,columnHeights[cursor.line]);
			}

			varrealX=rtlHelper.x(x);

			drawLegendBox(realX,y,legendItem);

			hitboxes[i].left=rtlHelper.leftForLtr(realX,hitboxes[i].width);
			hitboxes[i].top=y;

			//Filltheactuallabel
			fillText(realX,y,legendItem,textWidth);

			if(isHorizontal){
				cursor.x+=width+labelOpts.padding;
			}else{
				cursor.y+=itemHeight;
			}
		});

		helpers$1.rtl.restoreTextDirection(me.ctx,opts.textDirection);
	},

	/**
	*@private
	*/
	_getLegendItemAt:function(x,y){
		varme=this;
		vari,hitBox,lh;

		if(x>=me.left&&x<=me.right&&y>=me.top&&y<=me.bottom){
			//Seeifwearetouchingoneofthedatasetboxes
			lh=me.legendHitBoxes;
			for(i=0;i<lh.length;++i){
				hitBox=lh[i];

				if(x>=hitBox.left&&x<=hitBox.left+hitBox.width&&y>=hitBox.top&&y<=hitBox.top+hitBox.height){
					//Touchinganelement
					returnme.legendItems[i];
				}
			}
		}

		returnnull;
	},

	/**
	*Handleanevent
	*@private
	*@param{IEvent}event-Theeventtohandle
	*/
	handleEvent:function(e){
		varme=this;
		varopts=me.options;
		vartype=e.type==='mouseup'?'click':e.type;
		varhoveredItem;

		if(type==='mousemove'){
			if(!opts.onHover&&!opts.onLeave){
				return;
			}
		}elseif(type==='click'){
			if(!opts.onClick){
				return;
			}
		}else{
			return;
		}

		//Charteventalreadyhasrelativepositioninit
		hoveredItem=me._getLegendItemAt(e.x,e.y);

		if(type==='click'){
			if(hoveredItem&&opts.onClick){
				//usee.nativeforbackwardscompatibility
				opts.onClick.call(me,e.native,hoveredItem);
			}
		}else{
			if(opts.onLeave&&hoveredItem!==me._hoveredItem){
				if(me._hoveredItem){
					opts.onLeave.call(me,e.native,me._hoveredItem);
				}
				me._hoveredItem=hoveredItem;
			}

			if(opts.onHover&&hoveredItem){
				//usee.nativeforbackwardscompatibility
				opts.onHover.call(me,e.native,hoveredItem);
			}
		}
	}
});

functioncreateNewLegendAndAttach(chart,legendOpts){
	varlegend=newLegend({
		ctx:chart.ctx,
		options:legendOpts,
		chart:chart
	});

	core_layouts.configure(chart,legend,legendOpts);
	core_layouts.addBox(chart,legend);
	chart.legend=legend;
}

varplugin_legend={
	id:'legend',

	/**
	*Backwardcompatibility:since2.1.5,thelegendisregisteredasaplugin,making
	*Chart.Legendobsolete.Toavoidabreakingchange,weexporttheLegendaspartof
	*theplugin,whichonewillbere-exposedinthechart.jsfile.
	*https://github.com/chartjs/Chart.js/pull/2640
	*@private
	*/
	_element:Legend,

	beforeInit:function(chart){
		varlegendOpts=chart.options.legend;

		if(legendOpts){
			createNewLegendAndAttach(chart,legendOpts);
		}
	},

	beforeUpdate:function(chart){
		varlegendOpts=chart.options.legend;
		varlegend=chart.legend;

		if(legendOpts){
			helpers$1.mergeIf(legendOpts,core_defaults.global.legend);

			if(legend){
				core_layouts.configure(chart,legend,legendOpts);
				legend.options=legendOpts;
			}else{
				createNewLegendAndAttach(chart,legendOpts);
			}
		}elseif(legend){
			core_layouts.removeBox(chart,legend);
			deletechart.legend;
		}
	},

	afterEvent:function(chart,e){
		varlegend=chart.legend;
		if(legend){
			legend.handleEvent(e);
		}
	}
};

varnoop$2=helpers$1.noop;

core_defaults._set('global',{
	title:{
		display:false,
		fontStyle:'bold',
		fullWidth:true,
		padding:10,
		position:'top',
		text:'',
		weight:2000        //bydefaultgreaterthanlegend(1000)tobeabove
	}
});

/**
 *IMPORTANT:thisclassisexposedpubliclyasChart.Legend,backwardcompatibilityrequired!
 */
varTitle=core_element.extend({
	initialize:function(config){
		varme=this;
		helpers$1.extend(me,config);

		//Containshitboxesforeachdataset(indatasetorder)
		me.legendHitBoxes=[];
	},

	//Thesemethodsareorderedbylifecycle.Utilitiesthenfollow.

	beforeUpdate:noop$2,
	update:function(maxWidth,maxHeight,margins){
		varme=this;

		//UpdateLifecycle-Probablydon'twanttoeverextendoroverwritethisfunction;)
		me.beforeUpdate();

		//Absorbthemastermeasurements
		me.maxWidth=maxWidth;
		me.maxHeight=maxHeight;
		me.margins=margins;

		//Dimensions
		me.beforeSetDimensions();
		me.setDimensions();
		me.afterSetDimensions();
		//Labels
		me.beforeBuildLabels();
		me.buildLabels();
		me.afterBuildLabels();

		//Fit
		me.beforeFit();
		me.fit();
		me.afterFit();
		//
		me.afterUpdate();

		returnme.minSize;

	},
	afterUpdate:noop$2,

	//

	beforeSetDimensions:noop$2,
	setDimensions:function(){
		varme=this;
		//Settheunconstraineddimensionbeforelabelrotation
		if(me.isHorizontal()){
			//Resetpositionbeforecalculatingrotation
			me.width=me.maxWidth;
			me.left=0;
			me.right=me.width;
		}else{
			me.height=me.maxHeight;

			//Resetpositionbeforecalculatingrotation
			me.top=0;
			me.bottom=me.height;
		}

		//Resetpadding
		me.paddingLeft=0;
		me.paddingTop=0;
		me.paddingRight=0;
		me.paddingBottom=0;

		//ResetminSize
		me.minSize={
			width:0,
			height:0
		};
	},
	afterSetDimensions:noop$2,

	//

	beforeBuildLabels:noop$2,
	buildLabels:noop$2,
	afterBuildLabels:noop$2,

	//

	beforeFit:noop$2,
	fit:function(){
		varme=this;
		varopts=me.options;
		varminSize=me.minSize={};
		varisHorizontal=me.isHorizontal();
		varlineCount,textSize;

		if(!opts.display){
			me.width=minSize.width=me.height=minSize.height=0;
			return;
		}

		lineCount=helpers$1.isArray(opts.text)?opts.text.length:1;
		textSize=lineCount*helpers$1.options._parseFont(opts).lineHeight+opts.padding*2;

		me.width=minSize.width=isHorizontal?me.maxWidth:textSize;
		me.height=minSize.height=isHorizontal?textSize:me.maxHeight;
	},
	afterFit:noop$2,

	//SharedMethods
	isHorizontal:function(){
		varpos=this.options.position;
		returnpos==='top'||pos==='bottom';
	},

	//Actuallydrawthetitleblockonthecanvas
	draw:function(){
		varme=this;
		varctx=me.ctx;
		varopts=me.options;

		if(!opts.display){
			return;
		}

		varfontOpts=helpers$1.options._parseFont(opts);
		varlineHeight=fontOpts.lineHeight;
		varoffset=lineHeight/2+opts.padding;
		varrotation=0;
		vartop=me.top;
		varleft=me.left;
		varbottom=me.bottom;
		varright=me.right;
		varmaxWidth,titleX,titleY;

		ctx.fillStyle=helpers$1.valueOrDefault(opts.fontColor,core_defaults.global.defaultFontColor);//renderincorrectcolour
		ctx.font=fontOpts.string;

		//Horizontal
		if(me.isHorizontal()){
			titleX=left+((right-left)/2);//midpointofthewidth
			titleY=top+offset;
			maxWidth=right-left;
		}else{
			titleX=opts.position==='left'?left+offset:right-offset;
			titleY=top+((bottom-top)/2);
			maxWidth=bottom-top;
			rotation=Math.PI*(opts.position==='left'?-0.5:0.5);
		}

		ctx.save();
		ctx.translate(titleX,titleY);
		ctx.rotate(rotation);
		ctx.textAlign='center';
		ctx.textBaseline='middle';

		vartext=opts.text;
		if(helpers$1.isArray(text)){
			vary=0;
			for(vari=0;i<text.length;++i){
				ctx.fillText(text[i],0,y,maxWidth);
				y+=lineHeight;
			}
		}else{
			ctx.fillText(text,0,0,maxWidth);
		}

		ctx.restore();
	}
});

functioncreateNewTitleBlockAndAttach(chart,titleOpts){
	vartitle=newTitle({
		ctx:chart.ctx,
		options:titleOpts,
		chart:chart
	});

	core_layouts.configure(chart,title,titleOpts);
	core_layouts.addBox(chart,title);
	chart.titleBlock=title;
}

varplugin_title={
	id:'title',

	/**
	*Backwardcompatibility:since2.1.5,thetitleisregisteredasaplugin,making
	*Chart.Titleobsolete.Toavoidabreakingchange,weexporttheTitleaspartof
	*theplugin,whichonewillbere-exposedinthechart.jsfile.
	*https://github.com/chartjs/Chart.js/pull/2640
	*@private
	*/
	_element:Title,

	beforeInit:function(chart){
		vartitleOpts=chart.options.title;

		if(titleOpts){
			createNewTitleBlockAndAttach(chart,titleOpts);
		}
	},

	beforeUpdate:function(chart){
		vartitleOpts=chart.options.title;
		vartitleBlock=chart.titleBlock;

		if(titleOpts){
			helpers$1.mergeIf(titleOpts,core_defaults.global.title);

			if(titleBlock){
				core_layouts.configure(chart,titleBlock,titleOpts);
				titleBlock.options=titleOpts;
			}else{
				createNewTitleBlockAndAttach(chart,titleOpts);
			}
		}elseif(titleBlock){
			core_layouts.removeBox(chart,titleBlock);
			deletechart.titleBlock;
		}
	}
};

varplugins={};
varfiller=plugin_filler;
varlegend=plugin_legend;
vartitle=plugin_title;
plugins.filler=filler;
plugins.legend=legend;
plugins.title=title;

/**
 *@namespaceChart
 */


core_controller.helpers=helpers$1;

//@tododispatchthesehelpersintoappropriatedhelpers/helpers.*fileandwriteunittests!
core_helpers();

core_controller._adapters=core_adapters;
core_controller.Animation=core_animation;
core_controller.animationService=core_animations;
core_controller.controllers=controllers;
core_controller.DatasetController=core_datasetController;
core_controller.defaults=core_defaults;
core_controller.Element=core_element;
core_controller.elements=elements;
core_controller.Interaction=core_interaction;
core_controller.layouts=core_layouts;
core_controller.platform=platform;
core_controller.plugins=core_plugins;
core_controller.Scale=core_scale;
core_controller.scaleService=core_scaleService;
core_controller.Ticks=core_ticks;
core_controller.Tooltip=core_tooltip;

//Registerbuilt-inscales

core_controller.helpers.each(scales,function(scale,type){
	core_controller.scaleService.registerScaleType(type,scale,scale._defaults);
});

//Loadtoregisterbuilt-inadapters(assideeffects)


//Loadingbuilt-inplugins

for(varkinplugins){
	if(plugins.hasOwnProperty(k)){
		core_controller.plugins.register(plugins[k]);
	}
}

core_controller.platform.initialize();

varsrc=core_controller;
if(typeofwindow!=='undefined'){
	window.Chart=core_controller;
}

//DEPRECATIONS

/**
 *Providedforbackwardcompatibility,notavailableanymore
 *@namespaceChart.Chart
 *@deprecatedsinceversion2.8.0
 *@todoremoveatversion3
 *@private
 */
core_controller.Chart=core_controller;

/**
 *Providedforbackwardcompatibility,notavailableanymore
 *@namespaceChart.Legend
 *@deprecatedsinceversion2.1.5
 *@todoremoveatversion3
 *@private
 */
core_controller.Legend=plugins.legend._element;

/**
 *Providedforbackwardcompatibility,notavailableanymore
 *@namespaceChart.Title
 *@deprecatedsinceversion2.1.5
 *@todoremoveatversion3
 *@private
 */
core_controller.Title=plugins.title._element;

/**
 *Providedforbackwardcompatibility,useChart.pluginsinstead
 *@namespaceChart.pluginService
 *@deprecatedsinceversion2.1.5
 *@todoremoveatversion3
 *@private
 */
core_controller.pluginService=core_controller.plugins;

/**
 *Providedforbackwardcompatibility,inheritingfromChart.PlugingBasehasno
 *effect,insteadsimplycreate/registerpluginsviaplainJavaScriptobjects.
 *@interfaceChart.PluginBase
 *@deprecatedsinceversion2.5.0
 *@todoremoveatversion3
 *@private
 */
core_controller.PluginBase=core_controller.Element.extend({});

/**
 *Providedforbackwardcompatibility,useChart.helpers.canvasinstead.
 *@namespaceChart.canvasHelpers
 *@deprecatedsinceversion2.6.0
 *@todoremoveatversion3
 *@private
 */
core_controller.canvasHelpers=core_controller.helpers.canvas;

/**
 *Providedforbackwardcompatibility,useChart.layoutsinstead.
 *@namespaceChart.layoutService
 *@deprecatedsinceversion2.7.3
 *@todoremoveatversion3
 *@private
 */
core_controller.layoutService=core_controller.layouts;

/**
 *Providedforbackwardcompatibility,notavailableanymore.
 *@namespaceChart.LinearScaleBase
 *@deprecatedsinceversion2.8
 *@todoremoveatversion3
 *@private
 */
core_controller.LinearScaleBase=scale_linearbase;

/**
 *Providedforbackwardcompatibility,insteadweshouldcreateanewChart
 *bysettingthetypeintheconfig(`newChart(id,{type:'{chart-type}'}`).
 *@deprecatedsinceversion2.8.0
 *@todoremoveatversion3
 */
core_controller.helpers.each(
	[
		'Bar',
		'Bubble',
		'Doughnut',
		'Line',
		'PolarArea',
		'Radar',
		'Scatter'
	],
	function(klass){
		core_controller[klass]=function(ctx,cfg){
			returnnewcore_controller(ctx,core_controller.helpers.merge(cfg||{},{
				type:klass.charAt(0).toLowerCase()+klass.slice(1)
			}));
		};
	}
);

returnsrc;

})));
