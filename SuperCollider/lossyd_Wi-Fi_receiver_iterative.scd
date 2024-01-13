o = Server.default.options;
o.device = "Komplete Audio 6";
o.numOutputBusChannels = 8;
Server.default.reboot;

//"debug mode" - post all incoming OSC messages
OSCFunc.trace(true);
OSCFunc.trace(false);

/*
//-------------------------------------------------------------------////
Speaker Layouts Information

Name                | Number of Channels | Description
-------------------------------------------------------
\cube               | 8                  | 8 channel 3D layout
\domeVBAP           | 31                 | 31 channel speaker dome (SAT)
\iaiaVBAP           | 24                 | 24 channel speaker dome (IAIA)
\quadpanaz          | 4                  | 4 channel 2D layout
\stereoListener     | 2                  | Stereo panner
\VBAP1474           | 16                 | 16 channel speaker dome (IEM)
//---------------------------------------------------------------------*/


(
// define a server, SATIE needs it
s = Server.supernova.local;
// instantiate a SatieConfiguration. Here we will use a stereo spatializer
~satieConfiguration = SatieConfiguration.new(s, [\stereoListener]);
// list possible listeners:
~satieConfiguration.spatializers.keys;
// instantiate SATIE renderer and pass it the configuration
~satie = Satie.new(~satieConfiguration);
~satie.waitForBoot({
    // display some information
    s.meter;
    s.makeGui;
    s.plotTree;
})
)

(
// create 25 synths
25.do( { arg item;
    var nodename=("testNode"++"_"++item).asSymbol;
    var synth;
    synth = ~satie.makeSourceInstance(nodename.asSymbol, \saw, \default, synthArgs: [\attack, 0.2]);
	synth.set(\gainDB, rrand(-50, -5), \frequency, rrand(200, 2000));
});
)
(
~freqs = Array.newClear(25);
~amps = Array.newClear(25);
// Define a function to trigger the synth with the current frequency and amplitude values
~triggerSynth = {
    var ampsDbAmp, gainFactor=2;
    if(~freqs.every({ |item| item.notNil and: { item.isNumber }}) &&
       ~amps.every({ |item| item.notNil and: { item.isNumber }}), {
        ampsDbAmp = ~amps.collect { |db|
            if(db.notNil and: { db.isNumber }, { db.dbamp }, { 0 })
        };
		ampsDbAmp = ampsDbAmp.collect { |amp| amp * gainFactor };

		25.do({ |item|
				var nodename = ("testNode"++"_"++item).asSymbol;
				var freqValue, ampDbValue, aziDegValue;

				// Handling frequency value
				freqValue = if(~freqs[item-1].notNil and: { ~freqs[item-1].isNumber }, {
					~freqs[item-1];
				}, {
					440; // Replace <default_freq_value> with an appropriate number
				});

				// Handling amplitude value
				ampDbValue = if(~amps[item-1].notNil and: { ~amps[item-1].isNumber }, {
					~amps[item-1];
					//~amps[item-1].linlin(-80.0, -20, -50, -5).postln;
					//ampsDbAmp[item-1];
				}, {
					0.05; // Replace <default_amp_value> with a suitable number
				});

				// Handling azimuth degree (aziDeg) value
				aziDegValue = if(freqValue.notNil, {
					freqValue.linlin(20, 25000, -90, 90);
				}, {
					0; // Replace <default_aziDeg_value> with a proper number
				});

				// Update synth parameters using the checked values
				~satie.groupInstances[\default][nodename].set(
					\gainDB, (ampDbValue / 25).lag(0.1),
					\amp, ampDbValue,
					\frequency, freqValue,
					//\aziDeg, aziDegValue.lag(0.01),
					//\eleDeg, aziDegValue.lag(0.01),
					//\attack, 0.01,
					//\delayMs, rrand(1,100),
					//\lpHz, rrand(10000, 18000),
					//\hpHz, rrand(60, 200),
					\spread, rrand(0, 1)
				);

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
			\freq12, ~freqs[11],
			\freq13, ~freqs[12],
			\freq14, ~freqs[13],
			\freq15, ~freqs[14],
			\freq16, ~freqs[15],
			\freq17, ~freqs[16],
			\freq18, ~freqs[17],
			\freq19, ~freqs[18],
			\freq20, ~freqs[19],
			\freq21, ~freqs[20],
			\freq22, ~freqs[21],
			\freq23, ~freqs[22],
			\freq24, ~freqs[23],
			\freq25, ~freqs[24],
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
            \amp11, ampsDbAmp[10],
            \amp12, ampsDbAmp[11],
            \amp13, ampsDbAmp[12],
            \amp14, ampsDbAmp[13],
            \amp15, ampsDbAmp[14],
            \amp16, ampsDbAmp[15],
            \amp17, ampsDbAmp[16],
			\amp18, ampsDbAmp[17],
            \amp19, ampsDbAmp[18],
            \amp20, ampsDbAmp[19],
            \amp21, ampsDbAmp[20],
            \amp22, ampsDbAmp[21],
            \amp23, ampsDbAmp[22],
            \amp24, ampsDbAmp[23],
            \amp25, ampsDbAmp[24],
        );
			});

   });
};

// Create OSCFuncs for frequencies
(1..25).do { |i|
    OSCdef(("sweepFreq" ++ i).asSymbol, { |msg, time, addr, recvPort|
        ~freqs[i-1] = msg[1];
		//("Frequency " ++ i ++ ": " ++ msg[1]).postln;
        ~triggerSynth.value;
    }, '/sweep/' ++ i);
};

// Create OSCFuncs for amplitudes
(26..50).do { |i|
    OSCdef(("sweepAmp" ++ (i-25)).asSymbol, { |msg, time, addr, recvPort|
        ~amps[i-26] = msg[1]; // Assume that the dB values are already in the correct form
		//("Amplitude " ++ (i-25) ++ ": " ++ msg[1]).postln;
        ~triggerSynth.value;
    }, '/sweep/' ++ i);
};

~continuousSynth = Synth(\twentyFiveSineWaves);

)

  //------------------------------//
 // SinOsc synth without SATIE   //
//------------------------------//
(
SynthDef(\twentyFiveSineWaves, {
    arg freq1=24, freq2=32, freq3=43, freq4=58, freq5=77,
        freq6=103, freq7=138, freq8=184, freq9=246, freq10=328,
        freq11=438, freq12=584, freq13=779, freq14=1038, freq15=1385,
        freq16=1847, freq17=2464, freq18=3286, freq19=4383, freq20=5845,
        freq21=7795, freq22=10396, freq23=13864, freq24=18490, freq25=24660,
        amp1=0.1, amp2=0.1, amp3=0.1, amp4=0.1, amp5=0.1,
        amp6=0.1, amp7=0.1, amp8=0.1, amp9=0.1, amp10=0.1,
        amp11=0.1, amp12=0.1, amp13=0.1, amp14=0.1, amp15=0.1,
        amp16=0.1, amp17=0.1, amp18=0.1, amp19=0.1, amp20=0.1,
        amp21=0.1, amp22=0.1, amp23=0.1, amp24=0.1, amp25=0.1,
        pan1= -1, pan2= -0.92, pan3= -0.84, pan4= -0.76, pan5= -0.68,
        pan6= -0.6, pan7= -0.52, pan8= -0.44, pan9= -0.36, pan10= -0.28,
        pan11= -0.2, pan12= -0.12, pan13= -0.04, pan14=0.04, pan15=0.12,
        pan16=0.2, pan17=0.28, pan18=0.36, pan19=0.44, pan20=0.52,
        pan21=0.6, pan22=0.68, pan23=0.76, pan24=0.84, pan25=0.92;
    var osc1, osc2, osc3, osc4, osc5, osc6, osc7, osc8, osc9, osc10,
        osc11, osc12, osc13, osc14, osc15, osc16, osc17, osc18,
	    osc19, osc20, osc21, osc22, osc23, osc24, osc25, sound;

    // Create sine waves and apply pan
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
    osc12 = Pan2.ar(SinOsc.ar(freq12, 0, amp12), pan12);
    osc13 = Pan2.ar(SinOsc.ar(freq13, 0, amp13), pan13);
    osc14 = Pan2.ar(SinOsc.ar(freq14, 0, amp14), pan14);
    osc15 = Pan2.ar(SinOsc.ar(freq15, 0, amp15), pan15);
    osc16 = Pan2.ar(SinOsc.ar(freq16, 0, amp16), pan16);
    osc17 = Pan2.ar(SinOsc.ar(freq17, 0, amp17), pan17);
    osc18 = Pan2.ar(SinOsc.ar(freq18, 0, amp18), pan18);
    osc19 = Pan2.ar(SinOsc.ar(freq19, 0, amp19), pan19);
    osc20 = Pan2.ar(SinOsc.ar(freq20, 0, amp20), pan20);
    osc21 = Pan2.ar(SinOsc.ar(freq21, 0, amp21), pan21);
    osc22 = Pan2.ar(SinOsc.ar(freq22, 0, amp22), pan22);
    osc23 = Pan2.ar(SinOsc.ar(freq23, 0, amp23), pan23);
    osc24 = Pan2.ar(SinOsc.ar(freq24, 0, amp24), pan24);
    osc25 = Pan2.ar(SinOsc.ar(freq25, 0, amp25), pan25);

	// Mix the oscillators together
    sound = Mix.new([osc1, osc2, osc3, osc4, osc5, osc6, osc7,
		osc8,osc9, osc10, osc11, osc12, osc13, osc14, osc15, osc16,
		osc17, osc18, osc19, osc20, osc21, osc22, osc23, osc24,
		osc25]);
    sound = Limiter.ar(sound, 0.8, 0.01);

    // Output the sound
    Out.ar([0, 1], sound);
}).add;
)
(
SynthDef(\twentyFiveSineWaves, {

	| freqs = #[24, 32, 43, 58, 77, 103, 138, 184, 246, 328, 438,
		584, 779, 1038, 1385, 1847, 2464, 3286, 4383, 5845, 7795,
		10396, 13864, 18490, 24660],
	  amps = #[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1,
		0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1,
		0.1, 0.1, 0.1, 0.1]  |
	// Declare arrays for frequencies, amplitudes, and pans
    var pans, phases, oscs, sound;

	// Generate 25 pan values linearly spaced between -1 and 0.92
    pans = Array.fill(25, { |i| -1 + (i * (1.92 / 24)) });

	// Generate 25 phase values spaced between +-8pi
	phases = Array.fill(25, { |i| -8pi + (i * (16pi / 24)) });

    // Create sine waves and apply pan using a loop
    oscs = Array.fill(25, { |i|
        Pan2.ar(SinOsc.ar(freqs[i], 0, amps[i]), pans[i])
    });

    // Mix the oscillators together
    sound = Mix.new(oscs);
    sound = Limiter.ar(sound, 0.8, 0.01);

    // Output the sound
    Out.ar([0, 1], sound);
}).add;
)

(
~freqs = Array.newClear(25);
~amps = Array.newClear(25);

// Define a function to trigger the synth with the current frequency and amplitude values
~triggerSynth = {
    /*var ampsDbAmp, gainFactor=2;*/
    if(~freqs.every({ |item| item.notNil and: { item.isNumber }}), { /*&&
       ~amps.every({ |item| item.notNil and: { item.isNumber }}), {
        ampsDbAmp = ~amps.collect { |db|
            if(db.notNil and: { db.isNumber }, { db.dbamp }, { 0 })
        };
		ampsDbAmp = ampsDbAmp.collect { |amp| amp * gainFactor };*/

	25.do({ |item|
				var freqValue/*, ampValue*/;

				// Handling frequency value
				freqValue = if(~freqs[item-1].notNil and: { ~freqs[item-1].isNumber }, {
					~freqs[item-1];
				}, {
					440; // Replace <default_freq_value> with an appropriate number
				});
				/*// Handling amplitude value
				ampValue = if(~amps[item-1].notNil and: { ~amps[item-1].isNumber }, {
					~amps[item-1];
				}, {
					0.05; // Replace <default_amp_value> with a suitable number
				});*/

        ~continuousSynth.set(
					\freqs[item-1], freqValue[item-1],
					/*\amps[item-1], ampValue,*/
				);
		});
	});
};

// Create OSCFuncs for frequencies
(1..25).do { |i|
    OSCdef(("sweepFreq" ++ i).asSymbol, { |msg, time, addr, recvPort|
        ~freqs[i-1] = msg[1];
		("Frequency " ++ i ++ ": " ++ msg[1]).postln;
        ~triggerSynth.value;
    }, '/sweep/' ++ i);
};

// Create OSCFuncs for amplitudes
(26..50).do { |i|
    OSCdef(("sweepAmp" ++ (i-11)).asSymbol, { |msg, time, addr, recvPort|
        ~amps[i-12] = msg[1]; // Assume that the dB values are already in the correct form
		("Amplitude " ++ (i-11) ++ ": " ++ msg[1]).postln;
        ~triggerSynth.value;
    }, '/sweep/' ++ i);
};


~continuousSynth = Synth(\twentyFiveSineWaves);

)

(
// SynthDef with 25 sine wave oscillators
SynthDef(\twentyFiveSineWaves, { | freqs = #[24, 32, 43, 58, 77, 103,
	    138, 184, 246, 328, 438, 584, 779, 1038, 1385, 1847, 2464, 3286,
	    4383, 5845, 7795, 10396, 13864, 18490, 24660],
        phases = #[-25.13, -23.04, -20.94, -18.85, -16.76, -14.66, -12.57,
	    -10.47, -8.38, -6.28, -4.19, -2.09, 0.0, 2.09, 4.19, 6.28, 8.38,
	    10.47, 12.57, 14.66, 16.76, 18.85, 20.94, 23.04, 25.13],
        amps = #[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1,
		0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1,
		0.1, 0.1, 0.1, 0.1]  |
    var oscs, sound;

oscs = Array.fill(25, { |i| SinOsc.ar(freqs[i], phases[i], amps[i]) });

    sound = Mix.new(oscs) * 0.1; // Mix and control the overall volume
    Out.ar(0, sound);
}).add;

// Array to hold frequency values
~freqs = Array.newClear(25);
~amps = Array.newClear(25);
~phases = Array.newClear(25);

// Synth instance
~continuousSynth = Synth(\twentyFiveSineWaves);

// OSC message handling
(1..25).do { |i|
    OSCdef(("sweepFreq" ++ i).asSymbol, { |msg, time, addr, recvPort|
        ~freqs[i-1] = msg[1];
        //("Frequency " ++ i ++ ": " ++ msg[1]).postln;
        ~continuousSynth.set(\freqs, ~freqs);
    }, '/sweep/' ++ i);
};

(26..50).do { |i|
    OSCdef(("sweepAmp" ++ (i-25)).asSymbol, { |msg, time, addr, recvPort|
        ~amps[i-26] = msg[1].dbamp * 10;
		~phases[i-26] = msg[1].linlin(-70.0, -40.0, -8pi, 8pi);
		//("Amplitude " ++ (i-25) ++ ": " ++ msg[1]).postln;
		~continuousSynth.set(\amps, ~amps);
    }, '/sweep/' ++ i);
};
)
