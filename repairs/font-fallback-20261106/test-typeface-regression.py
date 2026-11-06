#!/usr/bin/env python3
"""Execute the actual Java reference-handling methods with native allocation stubbed."""
import pathlib,re,subprocess,tempfile,sys
root=pathlib.Path(__file__).resolve().parent
source=pathlib.Path(sys.argv[1]).read_text()
def method(name):
    match=re.search(r'    (?:public|private) (?:static )?(?:long|boolean|Typeface|void) '+name+r'\(',source)
    if not match:return ''
    begin=source.index('{',match.start());depth=1;end=begin+1
    while depth:
        depth += (source[end]=='{')-(source[end]=='}');end+=1
    return source[match.start():end].replace('@NonNull ','')
code='''import java.util.concurrent.atomic.AtomicReference;
import java.util.*;
public class Typeface {
 final long native_instance; final AtomicReference<Typeface> mPendingTypeface;
 static final String TAG="test";
 static class Log { static void w(String a,String b) {} }
 static final Object sDynamicCacheLock=new Object(), SYSTEM_FONT_MAP_LOCK=new Object();
 static class Cache {void evictAll() {}} static Cache sDynamicTypefaceCache=new Cache();
 static String sFontName; static final String DEFAULT_FAMILY="sans-serif";
 static final int BOLD=1, ITALIC=2, BOLD_ITALIC=3;
 static Typeface DEFAULT,DEFAULT_BOLD,SANS_SERIF,SERIF,MONOSPACE,sDefaultTypeface;
 static Map<String,Typeface> sSystemFontMap=new HashMap<>();
 static List<Typeface> defaults;
 static class FontController {
  static Typeface selected;
  static String getCurrentFontFamily() {return "missing-font";}
  static Typeface resolveBaseTypeface() {return selected;}
 }
 static Typeface create(Typeface t,int style) {return new Typeface(t.getNativeInstance()+style);}
 static void changeDefaultFontForTest(List<Typeface> fonts,List<Typeface> generics) {defaults=fonts;}
 Typeface(long n) {native_instance=n;mPendingTypeface=null;}
 Typeface(Typeface t) {native_instance=0;mPendingTypeface=new AtomicReference<>(t);}
'''+ '\n'.join(method(n) for n in ['getNativeInstance','updatePendingTypeface','resolveConcreteTypeface','changeFont'])+'''
 static void check(boolean b) {if(!b)throw new AssertionError();}
 public static void main(String[] args) {
  Typeface leaf=new Typeface(42L), a=new Typeface(leaf), b=new Typeface(a);
  // Missing custom-family fallback resolves to the same public placeholder.
  a.updatePendingTypeface(a);check(a.getNativeInstance()==42);
  // Aliased defaults and repeated configuration updates must never form cycles.
  for(int i=0;i<10000;i++) {a.updatePendingTypeface(b);b.updatePendingTypeface(a);}
  check(a.getNativeInstance()==42 && b.getNativeInstance()==42);
  Typeface next=new Typeface(77L);a.updatePendingTypeface(next);
  check(a.getNativeInstance()==77 && b.getNativeInstance()==42);
  check(!leaf.updatePendingTypeface(next));
  Typeface unresolved=new Typeface((Typeface)null);
  try {a.updatePendingTypeface(unresolved);throw new AssertionError();}
  catch(IllegalStateException expected) {} check(a.getNativeInstance()==77);
  Typeface cycle=new Typeface(leaf);cycle.mPendingTypeface.set(cycle);
  try {a.updatePendingTypeface(cycle);throw new AssertionError();}
  catch(IllegalStateException expected) {} check(a.getNativeInstance()==77);
  DEFAULT=new Typeface(leaf);SANS_SERIF=DEFAULT;DEFAULT_BOLD=new Typeface(new Typeface(43L));
  SERIF=new Typeface(50L);MONOSPACE=new Typeface(60L);FontController.selected=DEFAULT;
  for(int i=0;i<10000;i++)changeFont();
  check(DEFAULT.getNativeInstance()==42 && DEFAULT_BOLD.getNativeInstance()==43);
  check(defaults.get(0).mPendingTypeface==null);
  FontController.selected=next;changeFont();check(DEFAULT.getNativeInstance()==77);
  check(DEFAULT_BOLD.getNativeInstance()==78 && defaults.get(0)==next);
  System.out.println("PASS: self fallback, alias cycles, 10000 repeated updates, concrete replacement, unresolved/cyclic rejection");
  System.out.println("PASS: actual changeFont method, 10000 missing-font fallback changes, aliased public defaults, switching fonts");
 }
}
'''
with tempfile.TemporaryDirectory() as d:
    if len(sys.argv)>2:pathlib.Path(sys.argv[2]).write_text('package android.graphics;\n'+code)
    p=pathlib.Path(d)/'Typeface.java';p.write_text(code)
    subprocess.run(['javac',str(p)],check=True)
    r=subprocess.run(['java','-Xss256k','-cp',d,'Typeface'],capture_output=True,text=True)
    print(r.stdout or '\n'.join(r.stderr.splitlines()[:8]));sys.exit(r.returncode)
