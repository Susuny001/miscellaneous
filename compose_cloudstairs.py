#!/usr/bin/env python3
"""Three hand-written piano ideas using the uploaded reference's musical grammar.

Eight bars per idea, 100 BPM, flowing sixteenths over held left-hand voicings,
a written rise in bar four and a higher answering phrase in bar five.
No random pitch, rhythm, harmony, development or velocity generation.
"""
from __future__ import annotations
import argparse
import collections
import json
import math
from pathlib import Path
import re
import struct

BPM=100
PPQ=96
BAR=384
TOTAL_BARS=24
DURATION=57.6
STEM='Cloudstairs_100BPM_Piano'

# Each line is a newly written right-hand bar in scientific pitch notation.
# The source FLP's note names count octaves differently; MIDI C4 is 60 here.
IDEAS=[
 dict(name='旋律一 · 窗影',key='Db',reference_style='Db-major sixteenth-note figures; held dyads grouped 3+3+2',
  melody=[
   'Ab4 Eb5 F5 Db5 Ab5 F5 Eb5 Db5 Ab4 Eb5 F5 Db5 Eb5 Gb5 F5 Db5',
   'C5 F5 Ab5 G5 F5 C5 Eb5 F5 G5 Ab5 F5 Eb5 C5 Ab4',
   'F5 Db5 Bb4 F5 Ab5 F5 Eb5 Db5 F5 Ab5 Bb5 Ab5 F5 Eb5 Db5 Bb4',
   'Eb5 Ab4 C5 Eb5 F5 Eb5 Ab5 Bb5 C6 Bb5 Ab5 C6 Eb6 Db6 F6 Eb6',
   'F6 Eb6 Db6 Bb5 Db6 F6 Gb6 F6 Eb6 Db6 Bb5 Ab5 Bb5 Db6 Eb6 F6',
   'Db6 F6 Eb6 Bb5 F6 Db6 Bb5 Ab5 F5 Bb5 Db6 F6 Eb6 Db6 Bb5 F5',
   'Gb5 Db6 Bb5 Eb6 Gb6 F6 Eb6 Db6 C6 Eb6 Ab6 Gb6 F6 Eb6 C6 Ab5',
   'F6 Eb6 Db6 Ab5 F5 Eb5 Db5'],
  rhythms=['sixteenth','answer','sixteenth','sixteenth','sixteenth','sixteenth','sixteenth','cadence'],
  chords=[['Db3','Ab3','F4'],['F2','C3','Ab3'],['Bb2','F3','Db4'],['Ab2','Eb3','C4'],
          ['Gb2','Db3','Bb3'],['Bb2','F3','Db4'],[['Eb2','Bb2','Gb3'],['Ab2','Eb3','C4']],['Db3','Ab3','F4']],
  lh='332'),
 dict(name='旋律二 · 折线',key='Bm',reference_style='minor-key broken-chord dialogue and half-note left-hand dyads',
  melody=[
   'F#4 D5 C#5 B4 F#4 B4 D5 F#5 E5 D5 C#5 B4 D5 C#5 B4 F#4',
   'D5 B4 G4 B4 D5 F#5 E5 D5 B4 A4 B4 D5 F#5 D5',
   'A4 F#4 D5 C#5 A4 D5 F#5 E5 D5 A4 B4 C#5 D5 E5 F#5 A5',
   'C#5 A4 E5 C#5 B4 E5 A5 G5 F#5 E5 F#5 A5 A5 B5 C#6 E6',
   'G5 B5 E6 D6 B5 G5 F#5 E5 G5 B5 D6 C#6 B5 G5 F#5 E5',
   'B5 G5 D6 B5 A5 G5 F#5 D5 G5 B5 D6 E6 D6 B5 A5 G5',
   'C#6 A#5 F#5 E5 F#5 A#5 C#6 E6 F#6 E6 C#6 A#5 C#6 B5 A#5 F#5',
   'D6 C#6 B5 F#5 D5 C#5 B4'],
  rhythms=['sixteenth','answer','sixteenth','sixteenth','sixteenth','sixteenth','sixteenth','cadence'],
  chords=[['B2','F#3','D4'],['G2','D3','B3'],['D3','A3','D4'],['A2','E3','C#4'],
          ['E2','B2','G3'],['G2','D3','B3'],['F#2','C#3','A#3'],['B2','F#3','D4']],
  lh='halves'),
 dict(name='旋律三 · 晴隙',key='C',reference_style='major-key sixteenth-note figures answered by two bars of triplets',
  melody=[
   'G4 D5 E5 G5 B5 G5 E5 D5 C5 G4 D5 E5 G5 F5 E5 C5',
   'E5 C5 A4 C5 E5 G5 F5 E5 C5 D5 E5 A5 G5 E5',
   'A4 C5 F5 E5 D5 C5 A4 F4 A4 C5 D5 F5 G5 F5 E5 D5',
   'B4 D5 G5 F5 E5 D5 B4 G4 B4 D5 G5 A5 B5 D6 E6 G6',
   'E6 G6 D6 C6 E6 G5 B5 C6 D6 E6 C6 G5 A5 G5 E5 G5',
   'F5 A5 C6 E6 D6 C6 A5 C6 F6 E6 C6 A5',
   'D6 B5 G5 A5 B5 D6 F6 E6 D6 B5 A5 G5',
   'E6 D6 C6 G5 E5 D5 C5'],
  rhythms=['sixteenth','answer','sixteenth','sixteenth','sixteenth','triplets','triplets','cadence'],
  chords=[['C3','G3','E4'],['A2','E3','C4'],['F2','C3','A3'],['G2','D3','B3'],
          ['E3','G3','C4'],['F2','C3','A3'],['G2','D3','B3'],['C3','G3','E4']],
  lh='halves'),
]
RHYTHMS={
 'sixteenth':[24]*16,
 'answer':[24]*6+[48]+[24]*6+[48],
 'triplets':[32]*12,
 'cadence':[24,24,48,48,48,48,144],
}
ACCENTS=[96,84,89,85,94,86,91,85,95,84,88,86,93,85,90,84]


def pitch(name):
    match=re.fullmatch(r'([A-G])([b#]?)(-?\d+)',name)
    if not match:raise ValueError(name)
    letter,accidental,octave=match.groups()
    pc={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}[letter]
    return (int(octave)+1)*12+pc+{'':0,'b':-1,'#':1}[accidental]


def compose():
    notes=[];sections=[]
    def add(t,p,d,v,voice,section):
        notes.append(dict(t=int(t),p=pitch(p),d=int(d),v=int(v),voice=voice,section=section))
    for index,idea in enumerate(IDEAS):
        start=index*8*BAR
        sections.append(dict(name=idea['name'],start_bar=index*8,bars=8,kind=chr(65+index),
                             seconds=index*19.2,pattern=index+1,key=idea['key']))
        for bar,(melody,rhythm,chord) in enumerate(zip(idea['melody'],idea['rhythms'],idea['chords'])):
            offset=start+bar*BAR
            names=melody.split();lengths=RHYTHMS[rhythm]
            assert len(names)==len(lengths) and sum(lengths)==BAR,(index,bar)
            at=0
            for name,length in zip(names,lengths):
                step=min(15,at//24)
                velocity=ACCENTS[step]-(3 if bar>=4 else 0)
                if rhythm=='cadence' and at>=240:velocity=83
                add(offset+at,name,length,velocity,'melody',index)
                at+=length
            if isinstance(chord[0],list):
                for half,voicing in enumerate(chord):
                    add(offset+half*192,voicing[0],192,62,'bass',index)
                    for k,name in enumerate(voicing[1:]):add(offset+half*192,name,192,57+k*2,'inner',index)
            else:
                add(offset,chord[0],384,62,'bass',index)
                groups=[(0,144),(144,144),(288,96)] if idea['lh']=='332' else [(0,192),(192,192)]
                if bar==7:groups=[(0,384)]
                for group,(at,length) in enumerate(groups):
                    for k,name in enumerate(chord[1:]):
                        add(offset+at,name,length,57+k*2-(3 if group else 0),'inner',index)
    # Merge any physical unisons without altering the written melodic line.
    grouped=collections.defaultdict(list)
    for n in notes:grouped[(n['t'],n['p'])].append(n)
    merged=[]
    priority={'melody':2,'inner':1,'bass':0}
    for seq in grouped.values():
        n=max(seq,key=lambda x:priority[x['voice']]).copy()
        n['d']=max(x['d'] for x in seq);merged.append(n)
    notes=sorted(merged,key=lambda n:(n['t'],n['p']))
    by_pitch=collections.defaultdict(list)
    for n in notes:by_pitch[n['p']].append(n)
    for seq in by_pitch.values():
        for a,b in zip(seq,seq[1:]):a['d']=min(a['d'],b['t']-a['t'])
    return notes,sections


def write_midi(path,notes,sections,total_ticks=TOTAL_BARS*BAR,offset=0):
    import mido
    midi=mido.MidiFile(type=1,ticks_per_beat=PPQ)
    conductor=mido.MidiTrack();midi.tracks.append(conductor)
    conductor.append(mido.MetaMessage('set_tempo',tempo=600000,time=0))
    conductor.append(mido.MetaMessage('time_signature',numerator=4,denominator=4,time=0))
    key=sections[0].get('key','Db') if sections else 'Db'
    conductor.append(mido.MetaMessage('key_signature',key=key,time=0))
    previous=0
    for s in sections:
        at=s['start_bar']*BAR-offset
        if 0<=at<total_ticks:
            conductor.append(mido.MetaMessage('marker',text=f"Idea {s['pattern']}",time=at-previous));previous=at
    conductor.append(mido.MetaMessage('end_of_track',time=total_ticks-previous))
    tr=mido.MidiTrack();midi.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name',name='Original piano ideas',time=0))
    tr.append(mido.Message('program_change',program=0,channel=0,time=0))
    ev=[]
    for n in notes:
        if offset<=n['t']<offset+total_ticks:
            ev.extend([(n['t']-offset,1,n['p'],n['v']),
                       (min(n['t']+n['d']-offset,total_ticks),0,n['p'],0)])
    previous=0
    for tick,on,p,v in sorted(ev):
        tr.append(mido.Message('note_on' if on else 'note_off',channel=0,note=p,velocity=v,time=tick-previous));previous=tick
    tr.append(mido.MetaMessage('end_of_track',time=total_ticks-previous));midi.save(path)


def read_flp(path):
    raw=Path(path).read_bytes()
    if len(raw)<22 or raw[:4]!=b'FLhd' or raw[14:18]!=b'FLdt':
        raise ValueError('Not a binary FL Studio project; do not use a downloaded HTML page.')
    if struct.unpack_from('<I',raw,4)[0]!=6 or len(raw)!=22+struct.unpack_from('<I',raw,18)[0]:
        raise ValueError('Invalid FLP chunk length')
    events=[];pos=22
    while pos<len(raw):
        i=raw[pos];pos+=1
        if i<192:length=1 if i<64 else 2 if i<128 else 4
        else:
            length=0;shift=0
            while True:
                if pos>=len(raw) or shift>28:raise ValueError('Invalid event length')
                x=raw[pos];pos+=1;length|=(x&127)<<shift;shift+=7
                if x<128:break
        if pos+length>len(raw):raise ValueError('Truncated FLP event')
        events.append((i,raw[pos:pos+length]));pos+=length
    return events


def event(i,data):
    header=bytes([i])
    if i>=192:
        length=len(data)
        while length>=128:header+=bytes([(length&127)|128]);length>>=7
        header+=bytes([length])
    return header+data


def unicode(s):return (s+'\0').encode('utf-16le')


def write_flp(path,template,notes,sections):
    from repair_cloudstairs_flp import repair
    repair(template,path,notes,sections)


def render(notes,soundfont,path,duration=DURATION+1.8):
    import fluidsynth,numpy as np,soundfile as sf
    rate=44100
    fs=fluidsynth.Synth(gain=0.5,samplerate=rate)
    fs.setting('synth.chorus.active',0);fs.setting('synth.reverb.active',1)
    fs.setting('synth.reverb.room-size',0.35);fs.setting('synth.reverb.level',0.12)
    sfid=fs.sfload(str(soundfont));assert sfid>=0
    fs.program_select(0,sfid,0,0)
    ev=[]
    for n in notes:
        ev.extend([(round(n['t']/PPQ*0.6*rate),1,n['p'],n['v']),
                   (round((n['t']+n['d'])/PPQ*0.6*rate),0,n['p'],0)])
    position=0;peak=0.0
    with sf.SoundFile(str(path),'w',samplerate=rate,channels=2,subtype='PCM_24') as out:
        def emit(target):
            nonlocal position,peak
            while position<target:
                count=min(16384,target-position)
                samples=fs.get_samples(count).reshape(-1,2).astype(np.float32)/32768
                times=(position+np.arange(count))/rate
                samples*=np.clip((duration-times)/0.5,0,1)[:,None]
                peak=max(peak,float(np.abs(samples).max()));out.write(samples);position+=count
        for t,on,p,v in sorted(ev):
            emit(t)
            if on:fs.noteon(0,p,v)
            else:fs.noteoff(0,p)
        emit(round(duration*rate))
    fs.delete();return dict(seconds=duration,peak=peak,samplerate=rate)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=Path(__file__).parent)
    p.add_argument('--template',type=Path)
    p.add_argument('--soundfont',type=Path);p.add_argument('--render',type=Path)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    notes,sections=compose()
    write_midi(args.out/(STEM+'.mid'),notes,sections)
    for name,index in [('Theme_A',0),('Theme_B',1),('Theme_C_High',2)]:
        s=sections[index];write_midi(args.out/(STEM+'_'+name+'.mid'),notes,[s],8*BAR,s['start_bar']*BAR)
    template=args.template or args.out/(STEM+'.flp')
    if template.exists():write_flp(args.out/(STEM+'.flp'),template,notes,sections)
    report=dict(title='Cloudstairs - three short piano ideas',status='draft; awaiting native FL Studio and listening review',
                bpm=BPM,bars=TOTAL_BARS,duration=DURATION,note_count=len(notes),
                high_transition_bar_in_each_idea=4,high_answer_bar_in_each_idea=5,
                sections=sections,notes=notes)
    (args.out/'Cloudstairs_score.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    if args.render:
        if not args.soundfont:raise SystemExit('--soundfont required')
        print(render(notes,args.soundfont,args.render))
    print(json.dumps({k:v for k,v in report.items() if k!='notes'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
