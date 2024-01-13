o = Server.default.options;
o.device = "Scarlett 18i20 USB";
o.numOutputBusChannels = 8;
Server.default.boot;

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
~satieConfiguration = SatieConfiguration.new(s, [\cube]);
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
// create some test sound instances in the default group
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
					~amps[item-1] / 25;
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
					\gainDB, (ampDbValue / 25).lag(0.01),
					//\amp, ampDbValue,
					\frequency, freqValue.lag(0.99),
					\aziDeg, aziDegValue.lag(0.01),
					\eleDeg, aziDegValue.lag(0.01),
					//\attack, 0.01,
					//\delayMs, rrand(1,100),
					//\lpHz, rrand(10000, 18000),
					//\hpHz, rrand(60, 200),
					\spread, rrand(0, 1)
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
)

  //------------------------------//
 // SinOsc synth without SATIE   //
//------------------------------//


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
	pan11 = 1,
	trig1=17, trig2=17, trig3=17, trig4=17, trig5=17, trig6=17, trig7=17,
	trig8=17, trig9=17, trig10=17, trig11=17;
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



    // Mix the oscillators together
    sound = Mix.new([osc1, osc2, osc3, osc4, osc5, osc6, osc7, osc8, osc9,
		osc10, osc11]);
	//sound = JPverb.ar(sound, 0.2, size: 0.5);
	sound = Limiter.ar(sound, 0.8, 0.01);

	// Output the sound
	Out.ar([0, 1, 2, 3], sound);

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
			\freq1, ~freqs[0].postln,
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
            \amp11, ampsDbAmp[10],
        );
		20.do( {|item|
		var nodename=("testNode"++"_"++item);
		~satie.groupInstances[\default][nodename.asSymbol].set(
			\gainDB, ampsDbAmp[0],
			\aziDeg, rrand(-90, 90),
			\eleDeg, rrand(-90, 90),
			\delayMs, rrand(1,100),
			\lpHz, rrand(10000, 18000),
			\hpHz, rrand(60, 200),
			\spread, rrand(0, 1)
		);
	});

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