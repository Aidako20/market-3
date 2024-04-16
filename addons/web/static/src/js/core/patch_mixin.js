flectra.define("web.patchMixin",function(){
    "usestrict";

    /**
     *Thismoduledefinesandexportsthe'patchMixin'function.Thisfunction
     *returnsa'monkey-patchable'versionoftheES6Classgiveninarguments.
     *
     *   constpatchMixin=require('web.patchMixin');
     *   classMyClass{
     *       print(){
     *           console.log('MyClass');
     *       }
     *   }
     *   constMyPatchedClass=patchMixin(MyClass);
     *
     *
     *Apatchableclasshasa'patch'function,allowingtodefineapatch:
     *
     *   MyPatchedClass.patch("module_name.key",T=>
     *       classextendsT{
     *           print(){
     *               console.log('MyPatchedClass');
     *               super.print();
     *           }
     *       }
     *   );
     *
     *   constmyPatchedClass=newMyPatchedClass();
     *   myPatchedClass.print();//displays"MyPatchedClass"and"MyClass"
     *
     *
     *The'unpatch'functioncanbeusedtoremoveapatch,givenitskey:
     *
     *   MyPatchedClass.unpatch("module_name.key");
     */
    functionpatchMixin(OriginalClass){
        letunpatchList=[];
        classPatchableClassextendsOriginalClass{}

        PatchableClass.patch=function(name,patch){
            if(unpatchList.find(x=>x.name===name)){
                thrownewError(`Class${OriginalClass.name}alreadyhasapatch${name}`);
            }
            if(!Object.prototype.hasOwnProperty.call(this,'patch')){
                thrownewError(`Class${this.name}isnotpatchable`);
            }
            constSubClass=patch(Object.getPrototypeOf(this));
            unpatchList.push({
                name:name,
                elem:this,
                prototype:this.prototype,
                origProto:Object.getPrototypeOf(this),
                origPrototype:Object.getPrototypeOf(this.prototype),
                patch:patch,
            });
            Object.setPrototypeOf(this,SubClass);
            Object.setPrototypeOf(this.prototype,SubClass.prototype);
        };

        PatchableClass.unpatch=function(name){
            if(!unpatchList.find(x=>x.name===name)){
                thrownewError(`Class${OriginalClass.name}doesnothaveanypatch${name}`);
            }
            consttoUnpatch=unpatchList.reverse();
            unpatchList=[];
            for(letunpatchoftoUnpatch){
                Object.setPrototypeOf(unpatch.elem,unpatch.origProto);
                Object.setPrototypeOf(unpatch.prototype,unpatch.origPrototype);
            }
            for(letuoftoUnpatch.reverse()){
                if(u.name!==name){
                    PatchableClass.patch(u.name,u.patch);
                }
            }
        };
        returnPatchableClass;
    }

    returnpatchMixin;
});
