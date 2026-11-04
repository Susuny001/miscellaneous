#!/usr/bin/env python3
"""Cloudstairs: original solo-piano score, MIDI/FLP writer and offline renderer.

Python 3.12; rendering needs numpy, soundfile and pyfluidsynth/libfluidsynth.
MIDI output uses mido. No reference notes are used by this composer.
The existing Cloudstairs FLP supplies the piano's instrument settings only.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import random
import struct

BPM = 100
PPQ = 96
BAR = PPQ * 4
TOTAL_BARS = 500
DURATION = 1200.0
SEED = 20261104
STEM = "Cloudstairs_100BPM_Piano"
SCALE = (0, 2, 4, 5, 7, 9, 11)

# Degree zero is D4 (MIDI 62). Durations are sixteenth notes; -99 is a rest.
# Each theme is authored as a sixteen-bar question/answer, not sampled or
# transposed from the supplied reference. Variations develop these new themes.
A = [
 [(9,3),(11,1),(8,2),(9,2),(7,4),(-99,2),(8,2)],
 [(4,2),(7,1),(9,1),(8,2),(7,2),(5,3),(4,1),(2,2),(4,2)],
 [(5,2),(9,2),(8,3),(7,1),(6,2),(8,1),(7,1),(5,4)],
 [(7,4),(6,2),(4,2),(5,1),(6,1),(8,2),(7,2),(-99,2)],
 [(10,3),(9,1),(7,2),(5,2),(9,2),(10,1),(12,1),(11,4)],
 [(9,2),(7,2),(5,3),(7,1),(8,2),(9,2),(7,4)],
 [(8,2),(5,1),(3,1),(4,2),(6,2),(8,3),(7,1),(6,2),(4,2)],
 [(6,2),(8,2),(11,3),(10,1),(8,2),(6,2),(7,4)],
 [(9,2),(12,1),(11,1),(9,2),(8,2),(7,3),(9,1),(8,2),(4,2)],
 [(5,3),(7,1),(9,2),(12,2),(11,2),(9,2),(8,4)],
 [(10,2),(7,1),(5,1),(7,2),(9,2),(10,3),(12,1),(11,2),(9,2)],
 [(8,4),(-99,1),(6,1),(4,2),(6,2),(8,2),(11,4)],
 [(5,2),(8,2),(10,3),(9,1),(8,2),(7,1),(5,1),(3,4)],
 [(7,2),(9,2),(12,2),(11,2),(10,3),(9,1),(7,4)],
 [(8,2),(6,1),(4,1),(6,2),(8,2),(11,2),(10,2),(8,2),(6,2)],
 [(9,3),(8,1),(7,4),(4,2),(2,2),(7,4)],
]
B = [
 [(5,4),(-99,1),(6,1),(9,2),(8,3),(6,1),(5,4)],
 [(2,2),(5,1),(6,1),(9,2),(8,2),(6,2),(5,2),(3,4)],
 [(7,3),(4,1),(2,2),(4,2),(8,4),(7,2),(6,2)],
 [(4,2),(6,2),(8,1),(9,1),(11,2),(8,3),(6,1),(4,4)],
 [(5,2),(7,2),(10,3),(9,1),(7,2),(5,2),(3,4)],
 [(3,2),(5,1),(8,1),(10,2),(9,2),(8,2),(5,2),(4,4)],
 [(6,3),(8,1),(11,2),(9,2),(8,2),(6,2),(4,4)],
 [(9,2),(6,2),(5,4),(-99,2),(2,2),(5,4)],
 [(12,4),(11,2),(9,2),(8,3),(6,1),(9,4)],
 [(8,2),(6,1),(5,1),(2,2),(5,2),(9,2),(8,2),(6,4)],
 [(9,2),(7,2),(4,3),(2,1),(4,2),(7,2),(8,4)],
 [(11,3),(8,1),(6,2),(4,2),(6,2),(8,1),(9,1),(11,4)],
 [(10,2),(9,2),(7,2),(5,2),(3,4),(5,2),(7,2)],
 [(8,4),(-99,1),(5,1),(3,2),(5,2),(8,2),(10,4)],
 [(9,2),(8,2),(6,2),(4,2),(6,1),(8,1),(9,2),(6,4)],
 [(5,6),(2,2),(5,4),(-99,4)],
]
C = [
 [(11,4),(12,2),(9,1),(11,1),(14,3),(12,1),(11,4)],
 [(12,2),(9,2),(7,3),(9,1),(11,2),(12,2),(9,4)],
 [(10,3),(12,1),(14,2),(12,2),(10,2),(9,2),(7,4)],
 [(8,2),(11,2),(13,3),(12,1),(11,2),(8,2),(6,4)],
 [(12,2),(9,1),(7,1),(9,2),(12,2),(14,4),(12,2),(11,2)],
 [(10,4),(9,2),(7,2),(10,2),(12,2),(14,4)],
 [(13,3),(11,1),(8,2),(6,2),(8,1),(11,1),(13,2),(12,4)],
 [(11,2),(9,2),(7,6),(-99,2),(8,2),(9,2)],
 [(14,3),(12,1),(11,2),(9,2),(12,3),(11,1),(9,4)],
 [(11,2),(12,2),(14,2),(16,2),(14,3),(12,1),(11,4)],
 [(12,2),(10,1),(9,1),(7,2),(5,2),(7,2),(10,2),(12,4)],
 [(13,2),(11,2),(8,4),(11,2),(12,2),(13,4)],
 [(12,4),(9,2),(7,2),(5,3),(7,1),(9,4)],
 [(10,2),(12,2),(14,3),(12,1),(10,2),(9,2),(7,4)],
 [(11,2),(8,1),(6,1),(8,2),(11,2),(13,3),(12,1),(11,2),(8,2)],
 [(9,3),(8,1),(7,8),(-99,4)],
]
THEMES = {"A": A, "B": B, "C": C}

# Bass note and upper chord tones, voiced for a single pianist.
CHORDS = {
 "D9": (38,[57,62,66,69]), "DF": (42,[57,62,66,69]),
 "Bm": (35,[54,59,62,66]), "BA": (33,[54,59,62,66]),
 "G9": (31,[54,57,59,62]), "GB": (35,[55,59,62,66]),
 "Em": (40,[55,59,62,66]), "A": (33,[55,57,61,64]),
 "As": (33,[55,57,62,64]), "Fsm": (42,[57,61,64,69]),
 "DA": (33,[54,57,62,66]),
}
HARMONIES = {
 "A": ["D9","DF","Bm","BA","G9","GB","Em","A",
       "D9","Bm","G9","A","Em","G9","As","D9"],
 "B": ["Bm","Bm","D9","A","G9","Em","A","Bm",
       "Bm","Fsm","D9","A","G9","Em","As","Bm"],
 "C": ["D9","Bm","G9","A","Bm","G9","A","D9",
       "DF","Bm","G9","A","Bm","G9","As","D9"],
}

# start is computed; the central ascent ends at 09:55.200.
SECTIONS = [
 ("门前的光",8,"intro",0), ("窗边的回声 · 呈示",32,"A",0),
 ("窗边的回声 · 流动",32,"A",1), ("窗边的回声 · 应答",32,"A",2),
 ("转角",16,"link",0), ("未寄出的信 · 呈示",32,"B",0),
 ("未寄出的信 · 内声",32,"B",1), ("未寄出的信 · 展开",32,"B",2),
 ("悬停",16,"bridge",0), ("向云端 · 逐级升高",16,"rise",0),
 ("越过云沿 · 高音主题",32,"C",0), ("越过云沿 · 旋光",32,"C",1),
 ("越过云沿 · 长句",32,"C",2), ("远处的回答",16,"link",1),
 ("回声再现",32,"A",3), ("信笺展开",32,"B",3),
 ("云沿再现",32,"C",3), ("三条线的交会",32,"weave",0),
 ("落在窗台",12,"coda",0),
]

def degree(d):
    octave, i = divmod(d,7)
    return 62+octave*12+SCALE[i]

def compose():
    rng=random.Random(SEED)
    notes=[]; sections=[]; bar=0
    def add(pos,pitch,length,velocity,voice,section):
        # Small timing/velocity differences preserve the 100 BPM grid.
        jitter = rng.choice([0,0,0,1,-1]) if pos else 0
        start=max(0,int(round(pos+jitter)))
        length=max(8,int(round(length)))
        notes.append(dict(t=start,p=int(pitch),d=length,
                          v=max(28,min(111,int(velocity)+rng.randint(-3,3))),
                          voice=voice,section=section))
    for si,(name,bars,kind,variation) in enumerate(SECTIONS):
        sections.append(dict(name=name,start_bar=bar,bars=bars,kind=kind,
                             seconds=bar*2.4,pattern=si+1))
        for j in range(bars):
            pos=(bar+j)*BAR
            phase=j%16
            theme=kind if kind in THEMES else ("B" if kind in ("bridge","link") else "A")
            if kind=="weave": theme=("A","B","C","A")[j//8]
            chordname=HARMONIES[theme][phase]
            if kind=="intro": chordname=["D9","D9","GB","G9","Em","As","A","D9"][j]
            if kind=="rise": chordname=["Bm","Bm","G9","G9","Em","Em","As","A","D9","DF","G9","GB","Em","As","A","A"][j]
            if kind=="coda": chordname=["G9","GB","Em","As","D9","DF","G9","A","DA","As","D9","D9"][j]
            bass,upper=CHORDS[chordname]
            if kind=="B" and variation==0 and j<16:
                upper=[p-12 for p in upper]
            env=math.sin((j%8+0.5)/8*math.pi)
            dynamics=65+9*env
            if kind=="B": dynamics-=5
            if kind=="C": dynamics+=8
            if kind in ("intro","bridge"): dynamics-=11
            if kind=="rise": dynamics=62+j*1.3
            if kind=="coda": dynamics=69-j*2.2
            add(pos,bass,PPQ*1.8,dynamics-21,"bass",si)
            # Left-hand broken chords; variation is rhythmic and contrapuntal.
            arp=[0,2,1,3,1,2]
            times=[2,4,6,9,11,14]
            if variation==1: arp=[0,1,3,2,0,2];times=[2,5,7,10,12,14]
            if variation==2: arp=[1,2,0,3];times=[3,6,10,14]
            if variation==3: arp=[0,2,3,1,2];times=[2,5,8,11,14]
            if kind in ("intro","bridge","coda"):
                arp=[0,2,1]; times=[3,8,12]
            if kind=="coda" and j>=10:
                arp=[0,1,2,3];times=[0,0.16,0.32,0.48]
            for z,(at,ix) in enumerate(zip(times,arp)):
                dur=PPQ*(0.82 if kind!="coda" else 1.1)
                add(pos+at*24,upper[ix],dur,dynamics-20+(3 if z%3==0 else 0),"inner",si)
            if kind not in ("intro","bridge","coda"):
                add(pos+192,bass+12,PPQ*1.45,dynamics-25,"bass",si)

            if kind in THEMES or kind=="weave":
                cells=list(THEMES[theme][phase])
                # Second statement changes an interior gesture and phrase tail.
                developing=(j>=16)
                if developing and phase%4==1:
                    k=next((k for k,(d,l) in enumerate(cells) if l>=3 and d!=-99),None)
                    if k is not None:
                        d,l=cells[k];cells[k:k+1]=[(d,l-1),(d-1,1)]
                if variation in (1,3) and phase%4==2:
                    # Ornament a note, rather than quantising or copying a bar.
                    k=next((k for k,(d,l) in enumerate(cells) if l>=4 and d!=-99),None)
                    if k is not None:
                        d,l=cells[k];cells[k:k+1]=[(d,1),(d+1,1),(d,l-2)]
                if variation==1 and phase%2==0:
                    # A little sixteenth-note turn answers the reference's
                    # flowing texture, using only this score's own pitches.
                    k=next((k for k,(d,l) in enumerate(cells) if l==4 and d!=-99),None)
                    if k is not None:
                        d,l=cells[k];cells[k:k+1]=[(d,1),(d+2,1),(d+1,1),(d,1)]
                if variation==2 and phase%2==1 and len(cells)>2:
                    d,l=cells[0];d2,l2=cells[1]
                    if d!=-99 and d2!=-99 and l+l2<=6:
                        cells[:2]=[(d,l+l2)]
                if variation==2 and phase%4 in (0,3):
                    # More space in lyrical answers.
                    d,l=cells[-1]
                    if d!=-99 and l>=4: cells[-1:]=[(d,l-1),(-99,1)]
                offset=0
                # Only the central C entrance rises into the very high register.
                reg=0
                for k,(d,l) in enumerate(cells):
                    if d!=-99:
                        actual=d+reg
                        if theme=="B" and variation==0:actual=d-7 if j<16 else d
                        if developing and phase%4==3 and k==0:actual+=2
                        velocity=dynamics+8+(4 if offset%4==0 else -3)
                        add(pos+offset*24,degree(actual),l*24*(0.91 if l<=2 else 0.95),velocity,"melody",si)
                    offset+=l
                assert offset==16,(kind,phase,offset)
            elif kind=="rise":
                # Sixteen-bar written bridge: tessitura and density rise together.
                floor=0+(j//4)*2
                contour=[0,2,1,4,3,2,5,4]
                if j<4: contour=[0,2,1,4]
                for k,d in enumerate(contour):
                    step=16/len(contour)
                    add(pos+k*step*24,degree(floor+d),step*22,dynamics+6,"melody",si)
                if j==15:
                    # Dominant C-sharp resolves to high F-sharp at the entry.
                    notes[:]=[n for n in notes if not(n['section']==si and n['voice']=='melody' and n['t']>=pos+288)]
                    for k,d in enumerate([5,6,7,8]):add(pos+288+k*24,degree(d),22,dynamics+9,"melody",si)
            else:
                if kind=="intro":
                    cells=[(2+j%3,0,3),(4+j%3,6,2),(7+(j%2),12,3)]
                elif kind=="bridge":
                    cells=[(5+phase%3,0,5),(8-phase%2,8,4)]
                elif kind=="link":
                    cells=[(8-phase%3,0,3),(5+phase%2,5,2),(7-phase%4,10,4)]
                else:
                    cells=[(9-(j//3),0,5),(7-(j//4),8,5)]
                    if j>=10:cells=[(7,0,12)]
                for d,at,l in cells:add(pos+at*24,degree(d),l*24,dynamics+3,"melody",si)
        bar+=bars
    assert bar==TOTAL_BARS
    # A real ending within 20:00: leave room for the acoustic release.
    final_release=int((DURATION-2.0)/0.6*PPQ)
    notes=[n for n in notes if n['t']<final_release]
    for n in notes:n['d']=min(n['d'],final_release-n['t'])
    # One physical piano cannot strike the same key twice at the same instant.
    # Resolve unisons in favour of the melodic hand before trimming releases.
    priorities={'melody':3,'bass':2,'inner':1}
    grouped=collections.defaultdict(list)
    for n in notes:grouped[n['p']].append(n)
    clean=[]
    for seq in grouped.values():
        seq.sort(key=lambda n:n['t'])
        merged=[]
        for n in seq:
            if merged and n['t']-merged[-1]['t']<=2:
                a=merged[-1]
                chosen=n.copy() if priorities[n['voice']]>priorities[a['voice']] else a.copy()
                chosen['t']=min(a['t'],n['t']);chosen['d']=max(a['d'],n['d'])
                merged[-1]=chosen
            else:merged.append(n)
        clean.extend(merged)
    notes=clean
    # Prevent repeated pitches holding over their next attack on one piano.
    grouped=collections.defaultdict(list)
    for n in notes:grouped[n['p']].append(n)
    for seq in grouped.values():
        seq.sort(key=lambda n:n['t'])
        for a,b in zip(seq,seq[1:]):
            if b['t']>a['t']:a['d']=min(a['d'],b['t']-a['t'])
    notes.sort(key=lambda n:(n['t'],n['p']))
    return notes,sections

def write_midi(path,notes,sections,total_ticks=TOTAL_BARS*BAR,offset=0):
    import mido
    midi=mido.MidiFile(type=1,ticks_per_beat=PPQ)
    conductor=mido.MidiTrack();midi.tracks.append(conductor)
    conductor.append(mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(BPM),time=0))
    conductor.append(mido.MetaMessage('time_signature',numerator=4,denominator=4,time=0))
    conductor.append(mido.MetaMessage('key_signature',key='D',time=0))
    last=0
    for s in sections:
        at=s['start_bar']*BAR-offset
        if 0<=at<total_ticks:
            # Latin text keeps MIDI readable across FL Studio installations.
            conductor.append(mido.MetaMessage('marker',text=f"Part {s['pattern']:02d} / {s['kind']}",time=at-last));last=at
    conductor.append(mido.MetaMessage('end_of_track',time=total_ticks-last))
    # Keep all hands on one physical piano track. Ordering note-off before
    # note-on at equal ticks avoids cutting retriggers when voices meet.
    tr=mido.MidiTrack();midi.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name',name='Cloudstairs - Solo Piano',time=0))
    tr.append(mido.Message('program_change',program=0,channel=0,time=0))
    tr.append(mido.Message('control_change',control=7,value=100,channel=0,time=0))
    ev=[]
    for n in notes:
        if offset<=n['t']<offset+total_ticks:
            ev.append((n['t']-offset,1,n['p'],n['v']))
            ev.append((min(n['t']+n['d']-offset,total_ticks),0,n['p'],0))
    ev.sort();last=0
    for tick,on,p,v in ev:
        tr.append(mido.Message('note_on' if on else 'note_off',channel=0,note=p,velocity=v,time=tick-last));last=tick
    tr.append(mido.MetaMessage('end_of_track',time=total_ticks-last))
    midi.save(path)

def read_flp(path):
    b=Path(path).read_bytes()
    assert b[:4]==b'FLhd' and b[14:18]==b'FLdt'
    assert len(b)==22+struct.unpack_from('<I',b,18)[0]
    events=[];p=22
    while p<len(b):
        i=b[p];p+=1
        if i<192:n=1 if i<64 else 2 if i<128 else 4
        else:
            n=0;s=0
            while True:
                x=b[p];p+=1;n|=(x&127)<<s;s+=7
                if x<128:break
        events.append((i,b[p:p+n]));p+=n
    assert p==len(b)
    return events

def event(i,data):
    h=bytes([i])
    if i>=192:
        n=len(data)
        while n>=128:h+=bytes([(n&127)|128]);n>>=7
        h+=bytes([n])
    return h+data

def unicode(s):return (s+'\0').encode('utf-16le')

def write_flp(path,template,notes,sections):
    es=read_flp(template)
    first_pattern=next(k for k,(i,d) in enumerate(es) if i==65)
    globals_=es[:first_pattern]
    # Pick just the piano preset; no original musical data survives.
    blocks=[]
    starts=[k for k,(i,d) in enumerate(es) if i==64]
    for a in starts:
        # Pattern metadata can follow the final channel. Keep it out of the
        # instrument template so regenerating a project stays idempotent.
        z=next(k for k in range(a+1,len(es)) if es[k][0] in (64,65,99))
        block=es[a:z]
        name=next((d.decode('utf-16le').strip('\0') for i,d in block if i==203),'')
        if name in ('Basic Soft','Cloudstairs - Basic Soft'):blocks.append(block)
    if not blocks:raise ValueError('Piano preset is missing from the FLP template')
    # Reference channel 12 is the piano used by its three supplied melodies.
    piano=next((b for b in blocks if int.from_bytes(b[0][1],'little')==12),blocks[0])
    patched=[]
    for i,d in globals_:
        if i==156:d=struct.pack('<I',100000)
        if i==67:d=struct.pack('<H',1)
        if i in (9,10):d=b'\0'
        if i in (194,195,202,206,207,200):
            d=unicode({194:'Cloudstairs | Original solo piano',195:'Original composition. 100 BPM. Piano only. Central register ascent.',202:'',206:'Solo Piano',207:'',200:''}[i])
        patched.append((i,d))
    for s in sections:
        sid=s['pattern'];start=s['start_bar']*BAR;end=start+s['bars']*BAR
        selected=[n for n in notes if start<=n['t']<end]
        raw=b''.join(struct.pack('<IHHIHH8B',n['t']-start,0x4000,0,n['d'],n['p'],0,120,0,64,0,64,n['v'],128,128) for n in selected)
        patched += [(65,struct.pack('<H',sid)),(224,raw)]
    for i,d in piano:
        if i==64:d=struct.pack('<H',0)
        if i==203:d=unicode('Cloudstairs - Basic Soft')
        if i==143:d=struct.pack('<I',0) # route the only piano to Master
        patched.append((i,d))
    for s in sections:
        color=0x00b79964 if s['kind']!='C' else 0x00d4b8a0
        patched += [(65,struct.pack('<H',s['pattern'])),(193,unicode(s['name'])),
                    (150,struct.pack('<I',color)),(157,b'\xff'*4),(158,b'\xff'*4),
                    (164,struct.pack('<I',s['bars']*BAR))]
    arrangement_start=next(k for k,(i,d) in enumerate(es) if i==99)
    tail=es[arrangement_start:]
    oldplaylist=next(d for i,d in tail if i==233)
    # FL Studio 25 uses 80-byte playlist records. Keep the opaque trailing
    # compatibility fields from its own record and change only understood data.
    assert len(oldplaylist)%80==0
    clip_template=oldplaylist[:80]
    clips=[]
    for s in sections:
        clip=bytearray(clip_template)
        struct.pack_into('<IHHIHH',clip,0,s['start_bar']*BAR,20480,20480+s['pattern'],s['bars']*BAR,499,0)
        struct.pack_into('<II',clip,24,0,s['bars']*BAR)
        struct.pack_into('<I',clip,32,s['pattern'])
        clips.append(bytes(clip))
    for i,d in tail:
        if i==233:d=b''.join(clips)
        if i==241:d=unicode('Cloudstairs - 20 minutes - Piano only')
        if i==242:d=bytes(len(d)) # clear old arrangement selection/loop
        patched.append((i,d))
    payload=b''.join(event(i,d) for i,d in patched)
    Path(path).write_bytes(struct.pack('<4sIHHH',b'FLhd',6,0,1,PPQ)+b'FLdt'+struct.pack('<I',len(payload))+payload)

def render(notes,sf2,path):
    import fluidsynth
    import numpy as np
    import soundfile as sf
    rate=44100
    fs=fluidsynth.Synth(gain=0.5,samplerate=rate)
    fs.setting('synth.chorus.active',0)
    fs.setting('synth.reverb.active',1)
    fs.setting('synth.reverb.room-size',0.45)
    fs.setting('synth.reverb.damp',0.55)
    fs.setting('synth.reverb.width',25.0)
    fs.setting('synth.reverb.level',0.16)
    fs.setting('synth.polyphony',128)
    sfid=fs.sfload(str(sf2));assert sfid>=0
    fs.program_select(0,sfid,0,0)
    fs.cc(0,7,100);fs.cc(0,10,64)
    events=[]
    for n in notes:
        t=int(round(n['t']/PPQ*0.6*rate));off=int(round((n['t']+n['d'])/PPQ*0.6*rate))
        events.extend([(t,1,n['p'],n['v']),(off,0,n['p'],0)])
    events.sort();cursor=0;peak=0.0;sumsq=0.0;count=0
    with sf.SoundFile(str(path),'w',samplerate=rate,channels=2,subtype='PCM_24') as out:
        def emit(target):
            nonlocal cursor,peak,sumsq,count
            while cursor<target:
                length=min(16384,target-cursor)
                a=fs.get_samples(length).reshape(-1,2).astype(np.float32)/32768
                # The final natural release is gently faded, not abruptly cut.
                tt=(cursor+np.arange(length))/rate
                a*=np.minimum(1.0,np.maximum(0,(DURATION-tt)/1.3))[:,None]
                peak=max(peak,float(np.max(np.abs(a))))
                sumsq+=float(np.sum(a*a));count+=a.size
                out.write(a);cursor+=length
        for frame,on,p,v in events:
            emit(frame)
            if on:fs.noteon(0,p,v)
            else:fs.noteoff(0,p)
        emit(int(DURATION*rate))
    fs.delete()
    return dict(duration=DURATION,sample_rate=rate,peak=peak,rms=math.sqrt(sumsq/count))

def main():
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,default=Path(__file__).parent)
    a.add_argument('--template',type=Path);a.add_argument('--soundfont',type=Path)
    a.add_argument('--render',type=Path);args=a.parse_args()
    notes,sections=compose();out=args.out;out.mkdir(parents=True,exist_ok=True)
    write_midi(out/(STEM+'.mid'),notes,sections)
    for name,idx in [('Theme_A',1),('Theme_B',5),('Theme_C_High',10)]:
        s=sections[idx];write_midi(out/(STEM+'_'+name+'.mid'),notes,[s],32*BAR,s['start_bar']*BAR)
    template=args.template or out/(STEM+'.flp')
    if template.exists():write_flp(out/(STEM+'.flp'),template,notes,sections)
    report=dict(title='云阶 / Cloudstairs',bpm=BPM,bars=TOTAL_BARS,duration=DURATION,
                instruments=['Acoustic grand piano'],note_count=len(notes),seed=SEED,
                high_entry_seconds=595.2,sections=sections)
    (out/'Cloudstairs_score.json').write_text(json.dumps(dict(notes=notes,**report),ensure_ascii=False,indent=2)+'\n')
    if args.render:
        if not args.soundfont:raise SystemExit('--soundfont is required for rendering')
        report['render']=render(notes,args.soundfont,args.render)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
