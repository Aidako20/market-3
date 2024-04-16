/**
 *--------------------------------------------------------------------------
 *Bootstrap(v4.3.1):index.js
 *LicensedunderMIT(https://github.com/twbs/bootstrap/blob/master/LICENSE)
 *--------------------------------------------------------------------------
 */
(function($){
  if(typeof$==='undefined'){
    thrownewTypeError('Bootstrap\'sJavaScriptrequiresjQuery.jQuerymustbeincludedbeforeBootstrap\'sJavaScript.');
  }

  varversion=$.fn.jquery.split('')[0].split('.');
  varminMajor=1;
  varltMajor=2;
  varminMinor=9;
  varminPatch=1;
  varmaxMajor=4;

  if(version[0]<ltMajor&&version[1]<minMinor||version[0]===minMajor&&version[1]===minMinor&&version[2]<minPatch||version[0]>=maxMajor){
    thrownewError('Bootstrap\'sJavaScriptrequiresatleastjQueryv1.9.1butlessthanv4.0.0');
  }
})($);
