Server.default.options.inDevice_("BlackHole 2ch");
Server.default.options.outDevice_("BlackHole 2ch");
//"debug mode" - post all incoming OSC messages
OSCFunc.trace(true);
OSCFunc.trace(false);

(
SynthDef(\elevenSineWaves, {
    arg freq1=440, freq2=440, freq3=440, freq4=440, freq5=440,
	freq6=440, freq7=440, freq8=440, freq9=440, freq10=440, freq11=440,
        amp1=0.1, amp2=0.1, amp3=0.1, amp4=0.1, amp5=0.1,
        amp6=0.1, amp7=0.1, amp8=0.1, amp9=0.1, amp10=0.1, amp11=0.1,
        delay1=0.0, delay2=0.15, delay3=0.2, delay4=0.25, delay5=0.3,
        delay6=0.35, delay7=0.4, delay8=0.45, delay9=0.5, delay10=0.55,
	delay11=0.6,
        pan1 = -1, pan2 = -0.82, pan3 = -0.64, pan4 = -0.46, pan5 = -0.28,
        pan6 = -0.1, pan7 = 0.08, pan8 = 0.26, pan9 = 0.44, pan10 = 0.62,
	pan11 = 1;
    var osc1, osc2, osc3, osc4, osc5, osc6, osc7, osc8, osc9, osc10,
	osc11, oscs, sound;

    //Create sine waves and apply pan
    osc1 = Pan2.ar(SinOsc.ar(freq1, 0, amp1), pan1);
    osc2 = Pan2.ar(SinOsc.ar(freq2, 0, amp2), pan2);
    osc3 = Pan2.ar(SinOsc.ar(freq3, 0, amp3), pan3);
    osc4 = Pan2.ar(SinOsc.ar(freq4, 0, amp4), pan4);
    osc5 = Pan2.ar(SinOsc.ar(freq5, 0, amp5), pan5);
    osc6 = Pan2.ar(SinOsc.ar(freq6, 0, amp6), pan6);
    osc7 = Pan2.ar(SinOsc.ar(freq7, 0, amp7), pan7);
    osc8 = Pan2.ar(SinOsc.ar(freq8, 0, amp8), pan8);
    osc9 = Pan2.ar(SinOsc.ar(freq9, 0, amp9), pan9);
    osc10 = Pan2.ar(SinOsc.ar(freq10, 0, amp10), pan10);
    osc11 = Pan2.ar(SinOsc.ar(freq11, 0, amp11), pan11);


    // Apply delays to each panned oscillator
    osc1 = DelayN.ar(osc1, 0.5, delay1);
    osc2 = DelayN.ar(osc2, 0.5, delay2);
    osc3 = DelayN.ar(osc3, 0.5, delay3);
    osc4 = DelayN.ar(osc4, 0.5, delay4);
    osc5 = DelayN.ar(osc5, 0.5, delay5);
    osc6 = DelayN.ar(osc6, 0.5, delay6);
    osc7 = DelayN.ar(osc7, 0.5, delay7);
    osc8 = DelayN.ar(osc8, 0.5, delay8);
    osc9 = DelayN.ar(osc9, 0.5, delay9);
    osc10 = DelayN.ar(osc10, 0.5, delay10);
    osc11 = DelayN.ar(osc11, 0.5, delay11);

    // Mix the oscillators together
    sound = Mix.new([osc1, osc2, osc3, osc4, osc5, osc6, osc7, osc8, osc9,
		osc10, osc11]);
	sound = JPverb.ar(sound, 0.2, size: 0.5);
	sound = Limiter.ar(sound, 0.8, 0.01);

	// Output the sound
	Out.ar([0, 1], sound);

}).add;
)

(
~freqs = Array.newClear(11);
~amps = Array.newClear(11);

// Define a function to trigger the synth with the current frequency and amplitude values
~triggerSynth = {
    var ampsDbAmp, gainFactor=2;
    if(~freqs.every({ |item| item.notNil and: { item.isNumber }}) &&
       ~amps.every({ |item| item.notNil and: { item.isNumber }}), {
        ampsDbAmp = ~amps.collect { |db|
            if(db.notNil and: { db.isNumber }, { db.dbamp }, { 0 })
        };
		ampsDbAmp = ampsDbAmp.collect { |amp| amp * gainFactor };
        ~continuousSynth.set(
			\freq1, ~freqs[0],
			\freq2, ~freqs[1],
			\freq3, ~freqs[2],
			\freq4, ~freqs[3],
			\freq5, ~freqs[4],
			\freq6, ~freqs[5],
			\freq7, ~freqs[6],
			\freq8, ~freqs[7],
			\freq9, ~freqs[8],
			\freq10, ~freqs[9],
			\freq11, ~freqs[10],
            \amp1, ampsDbAmp[0],
            \amp2, ampsDbAmp[1],
            \amp3, ampsDbAmp[2],
            \amp4, ampsDbAmp[3],
            \amp5, ampsDbAmp[4],
            \amp6, ampsDbAmp[5],
			\amp7, ampsDbAmp[6],
            \amp8, ampsDbAmp[7],
            \amp9, ampsDbAmp[8],
            \amp10, ampsDbAmp[9],
            \amp11, ampsDbAmp[10]
        );

    });
};

// Create OSCFuncs for frequencies
(1..11).do { |i|
    OSCdef(("sweepFreq" ++ i).asSymbol, { |msg, time, addr, recvPort|
        ~freqs[i-1] = msg[1];
		("Frequency " ++ i ++ ": " ++ msg[1]).postln;
        ~triggerSynth.value;
    }, '/sweep/' ++ i);
};

// Create OSCFuncs for amplitudes
(12..22).do { |i|
    OSCdef(("sweepAmp" ++ (i-11)).asSymbol, { |msg, time, addr, recvPort|
        ~amps[i-12] = msg[1]; // Assume that the dB values are already in the correct form
		("Amplitude " ++ (i-11) ++ ": " ++ msg[1]).postln;
        ~triggerSynth.value;
    }, '/sweep/' ++ i);
};


~continuousSynth = Synth(\elevenSineWaves);

)










----TONES AND IDS------


s.boot;

~networkName = OSCFunc({ |msg, time, addr, recvPort|
    msg.postln;
}, '/networks/1');

~ssri = OSCFunc({ |msg, time, addr, recvPort|
    msg.postln;
}, '/networks/3');

(
SynthDef.new(\tone, {
	var sig, env;
	env = Env.adsr.kr(0, \gate.kr(0));
	sig = LFTri.ar(\freq.kr(300));
	sig = Pan2.ar(sig, \pan.kr(0), \amp.kr(0.2));
	sig = sig * env;
	Out.ar(\out.kr(0), sig);
}).add;
)

x = Synth.new(\tone, [\gate, 1]);
x.set(\gate, 0);

(
x = Synth.new(\tone, [\gate, 0]);

OSCdef.new(\listener, {
	arg msg;
	x.set(\gate, msg[1]);
}, '/1/push1', nil, 57120);
)

(
~scale = [0,12,24,36,48].collect({
	arg n;
	n + 35 + Scale.minorPentatonic.degrees
}).flatten;

~synths = ~scale.collect({
	arg note;
	Synth(\tone, [\freq, note.midicps]);
});

(1..5).do({
	arg row;
	(1..5).do({
		arg col;
		var index = (row-1) * 5 + (col-1);
		OSCdef.new(("multi"++row++col).asSymbol, {
			arg msg;
			~synths.at(index).set(\gate, msg[1])
		}, "/1/multipush1/" ++ row ++ "/" ++ col, nil, 57120);
	});
});
)

s.defaultGroup.set(\gate, 0);

OSCdef.freeAll;
OSCFunc.trace(false);
