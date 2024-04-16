/*
ThefollowingscriptcanbeusedtoconvertSVGsexportedfromillustratorinto
aformatthat'scompatiblewiththeshapesystem.Itrunswithnodejs.Some
manualconversionmaybenecessary.
*/

constfs=require('fs');
constpath=require('path');

constpalette={
    '1':'#3AADAA',
    '2':'#7C6576',
    '3':'#F6F6F6',
    '4':'#FFFFFF',
    '5':'#383E45',
};

constpositions=['top','left','bottom','right','center','stretch'];

constdirectories=fs.readdirSync(__dirname).filter(nodeName=>{
    returnnodeName[0]!=='.'&&fs.lstatSync(path.join(__dirname,nodeName)).isDirectory();
});
constfiles=directories.flatMap(dirName=>{
    returnfs.readdirSync(path.join(__dirname,dirName))
        .filter(fileName=>fileName.endsWith('.svg'))
        .map(fileName=>path.join(__dirname,dirName,fileName));
});

constshapes=[];
files.filter(f=>f.endsWith('svg')).forEach(filePath=>{
    constsvg=String(fs.readFileSync(filePath));
    constfileName=filePath.match(/([^/]+)$/)[1];

    constcolors=svg.match(/#[0-9A-F]{3,}/gi);
    constnonPaletteColors=colors&&colors.filter(color=>!Object.values(palette).includes(color.toUpperCase()));
    constshape={
        svg,
        name:fileName.split(/[.-]/)[0],
        page:filePath.slice(__dirname.length+1,-fileName.length-1),
        colors:Object.keys(palette).filter(num=>newRegExp(palette[num],'i').test(svg)),
        position:positions.filter(pos=>fileName.includes(pos)),
        nonIsometric:fileName.includes('+'),
        nonPaletteColors:nonPaletteColors&&nonPaletteColors.length?nonPaletteColors.join(''):null,
        containsImage:svg.includes('<image'),
        repeatY:fileName.includes('repeaty'),
    };
    shape.optionXML=`<we-buttondata-shape="web_editor/${shape.page}/${shape.name}"data-select-label="${shape.page}${shape.name}"/>`;
    if(shape.position[0]==='stretch'){
        shape.position=['center'];
        shape.size='100%100%';
    }else{
        shape.size='100%auto';
    }
    shape.scss=`'${shape.page}/${shape.name}':('position':${shape.position[0]},'size':${shape.size},'colors':(${shape.colors.join(',')}),'repeat-y':${shape.repeatY})`;
    shapes.push(shape);
});
constxml=shapes.map(shape=>shape.optionXML).join('\n');
constscss=shapes.map(shape=>shape.scss).join(',\n');
constnonConformShapes=shapes.flatMap(shape=>{
    constviolations={};
    letinvalid=false;
    //Notsureifwewantthischeck,edistilltryingtoseeifshecandoshadowswithoutembeddingPNGs
    //if(shape.containsImage){
    //    violations.containsImage=shape.containsImage;
    //    invalid=true;
    //}
    if(shape.nonIsometric){
        violations.nonIsometric=shape.nonIsometric;
        invalid=true;
    }
    if(shape.nonPaletteColors){
        violations.nonPaletteColors=shape.nonPaletteColors;
        invalid=true;
    }
    if(shape.position.length>1||shape.position.length==0){
        violations.position=shape.position;
        invalid=true;
    }
    if(!invalid){
        return[]
    }
    return[[shape,violations]];
});
console.log('Thefollowingshapesarenotconform:',nonConformShapes);

constconvertDir='./.converted';
fs.mkdirSync(convertDir);
constconvertedPath=path.join(__dirname,convertDir);
fs.writeFileSync(path.join(convertedPath,'options.xml'),xml);
fs.writeFileSync(path.join(convertedPath,'variables.scss'),scss);
shapes.forEach(shape=>{
    constpageDir=path.join(convertedPath,shape.page);
    if(!fs.existsSync(pageDir)){
        fs.mkdirSync(pageDir);
    }
    fs.writeFileSync(path.join(pageDir,shape.name+'.svg'),shape.svg);
});
