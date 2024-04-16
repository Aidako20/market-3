flectra.define('point_of_sale.ClassRegistry',function(require){
    'usestrict';

    /**
     ***Usage:**
     *```
     *constRegistry=newClassRegistry();
     *
     *classA{}
     *Registry.add(A);
     *
     *constAExt1=A=>classextendsA{}
     *Registry.extend(A,AExt1)
     *
     *constB=A=>classextendsA{}
     *Registry.addByExtending(B,A)
     *
     *constAExt2=A=>classextendsA{}
     *Registry.extend(A,AExt2)
     *
     *Registry.get(A)
     *//abovereturns:AExt2->AExt1->A
     *//Basically,'A'intheregistrypointsto
     *//theinheritancechainabove.
     *
     *Registry.get(B)
     *//abovereturns:B->AExt2->AExt1->A
     *//EventhoughBextendsAbeforeapplyingall
     *//theextensionsofA,whengettingitfromthe
     *//registry,thereturnpointstoaclasswith
     *//inheritancechainthatincludesalltheextensions
     *//of'A'.
     *
     *Registry.freeze()
     *//Example'B'aboveislazy.Basically,itisonly
     *//computedwhenwecall`get`fromtheregistry.
     *//Ifweknowthatnomoredynamicinheritanceswillhappen,
     *//wecanfreezetheregistryandcachethefinalform
     *//ofeachclassintheregistry.
     *```
     *
     *IMPROVEMENT:
     **Sofar,mixincanbeaccomplishedbycreatingamethod
     * thetakesaclassandreturnsaclassexpression.Thisisthen
     * usedbeforetheextendskeywordlikeso:
     *
     * ```js
     * classA{}
     * Registry.add(A)
     * constMixin=x=>classextendsx{}
     * //                         applymixin
     * //                             |
     * //                             v
     * constB=x=>classextendsMixin(x){}
     * Registry.addByExtending(B,A)
     * ```
     *
     * Intheexample,`|B|=>B->Mixin->A`,andthisisprettyconvenient
     * already.However,thiscanstillbeimprovedsinceclassesareonly
     * compiledafter`Registry.freeze()`.Perhaps,wecanmakethe
     * Mixinsextensibleaswell,suchasso:
     *
     * ```
     * classA{}
     * Registry.add(A)
     * constMixin=x=>classextendsx{}
     * Registry.add(Mixin)
     * constOtherMixin=x=>classextendsx{}
     * Registry.add(OtherMixin)
     * constB=x=>classextendsx{}
     * Registry.addByExtending(B,A,[Mixin,OtherMixin])
     * constExtendMixin=x=>classextendsx{}
     * Registry.extend(Mixin,ExtendMixin)
     * ```
     *
     * Intheabove,after`Registry.freeze()`,
     * `|B|=>B->OtherMixin->ExtendMixin->Mixin->A`
     */
    classClassRegistry{
        constructor(){
            //basenamemap
            this.baseNameMap={};
            //Objectthatmaps`baseClass`totheclassimplementationextendedin-place.
            this.includedMap=newMap();
            //Objectthatmaps`baseClassCB`tothearrayofcallbackstogeneratetheextendedclass.
            this.extendedCBMap=newMap();
            //Objectthatmaps`baseClassCB`extendedclasstothe`baseClass`ofitssuperintheincludedMap.
            this.extendedSuperMap=newMap();
            //Forfasteraccess,wecan`freeze`theregistrysothatinsteadofdynamicallygenerating
            //theextendedclasses,itistakenfromthecacheinstead.
            this.cache=newMap();
        }
        /**
         *AddanewclassintheRegistry.
         *@param{Function}baseClass`class`
         */
        add(baseClass){
            this.includedMap.set(baseClass,[]);
            this.baseNameMap[baseClass.name]=baseClass;
        }
        /**
         *AddanewclassintheRegistrybasedonotherclass
         *intheregistry.
         *@param{Function}baseClassCB`class->class`
         *@param{Function}base`class|class->class`
         */
        addByExtending(baseClassCB,base){
            this.extendedCBMap.set(baseClassCB,[baseClassCB]);
            this.extendedSuperMap.set(baseClassCB,base);
            this.baseNameMap[baseClassCB.name]=baseClassCB;
        }
        /**
         *Extendin-placeaclassintheregistry.E.g.
         *```
         *//Usingthefollowingnotation:
         *// *|A|- compiledclassintheregistry
         *// * A - classoranextensioncallback
         *// *|A|=>A2->A1->A
         *//      - theabovemeans,compiledclassA
         *//         pointstotheclassinheritancederivedfrom
         *//         A2(A1(A))
         *
         *classA{};
         *Registry.add(A);
         *//|A|=>A
         *
         *letA1=x=>classextendsx{};
         *Registry.extend(A,A1);
         *//|A|=>A1->A
         *
         *letB=x=>classextendsx{};
         *Registry.addByExtending(B,A);
         *//|B|=>B->|A|
         *//|B|=>B->A1->A
         *
         *letB1=x=>classextendsx{};
         *Registry.extend(B,B1);
         *//|B|=>B1->B->|A|
         *
         *letC=x=>classextendsx{};
         *Registry.addByExtending(C,B);
         *//|C|=>C->|B|
         *
         *letB2=x=>classextendsx{};
         *Registry.extend(B,B2);
         *//|B|=>B2->B1->B->|A|
         *
         *//Overall:
         *//|A|=>A1->A
         *//|B|=>B2->B1->B->A1->A
         *//|C|=>C->B2->B1->B->A1->A
         *```
         *@param{Function}base`class|class->class`
         *@param{Function}extensionCB`class->class`
         */
        extend(base,extensionCB){
            if(typeofbase==='string'){
                base=this.baseNameMap[base];
            }
            letextensionArray;
            if(this.includedMap.get(base)){
                extensionArray=this.includedMap.get(base);
            }elseif(this.extendedCBMap.get(base)){
                extensionArray=this.extendedCBMap.get(base);
            }else{
                thrownewError(
                    `'${base.name}'isnotintheRegistry.AddittoRegistrybeforeextending.`
                );
            }
            extensionArray.push(extensionCB);
            constlocOfNewExtension=extensionArray.length-1;
            constself=this;
            constoldCompiled=this.isFrozen?this.cache.get(base):null;
            return{
                remove(){
                    extensionArray.splice(locOfNewExtension,1);
                    self._recompute(base,oldCompiled);
                },
                compile(){
                    self._recompute(base);
                }
            };
        }
        _compile(base){
            letres;
            if(this.includedMap.has(base)){
                res=this.includedMap.get(base).reduce((acc,ext)=>ext(acc),base);
            }else{
                constsuperClass=this.extendedSuperMap.get(base);
                constextensionCBs=this.extendedCBMap.get(base);
                res=extensionCBs.reduce((acc,ext)=>ext(acc),this._compile(superClass));
            }
            Object.defineProperty(res,'name',{value:base.name});
            returnres;
        }
        /**
         *Returnthecompiledclass(containingalltheextensions)ofthebaseclass.
         *@param{Function}base`class|class->class`functionusedinaddingtheclass
         */
        get(base){
            if(typeofbase==='string'){
                base=this.baseNameMap[base];
            }
            if(this.isFrozen){
                returnthis.cache.get(base);
            }
            returnthis._compile(base);
        }
        /**
         *Usesthecallbacksregisteredintheregistrytocompiletheclasses.
         */
        freeze(){
            //Step:Compilethe`includedclasses`.
            for(let[baseClass,extensionCBs]ofthis.includedMap.entries()){
                constcompiled=extensionCBs.reduce((acc,ext)=>ext(acc),baseClass);
                this.cache.set(baseClass,compiled);
            }

            //Step:Compilethe`extendedclasses`basedon`includedclasses`.
            //Alsogatherthosethearebasedon`extendedclasses`.
            constremaining=[];
            for(let[baseClassCB,extensionCBArray]ofthis.extendedCBMap.entries()){
                constcompiled=this.cache.get(this.extendedSuperMap.get(baseClassCB));
                if(!compiled){
                    remaining.push([baseClassCB,extensionCBArray]);
                    continue;
                }
                constextendedClass=extensionCBArray.reduce(
                    (acc,extensionCB)=>extensionCB(acc),
                    compiled
                );
                this.cache.set(baseClassCB,extendedClass);
            }

            //Step:Compilethe`extendedclasses`basedon`extendedclasses`.
            for(let[baseClassCB,extensionCBArray]ofremaining){
                constcompiled=this.cache.get(this.extendedSuperMap.get(baseClassCB));
                constextendedClass=extensionCBArray.reduce(
                    (acc,extensionCB)=>extensionCB(acc),
                    compiled
                );
                this.cache.set(baseClassCB,extendedClass);
            }

            //Step:Setthenameofthecompiledclassess
            for(let[base,compiledClass]ofthis.cache.entries()){
                Object.defineProperty(compiledClass,'name',{value:base.name});
            }

            //Step:Settheflagtotrue;
            this.isFrozen=true;
        }
        _recompute(base,old){
            if(typeofbase==='string'){
                base=this.baseNameMap[base];
            }
            returnold?old:this._compile(base);
        }
    }

    returnClassRegistry;
});
