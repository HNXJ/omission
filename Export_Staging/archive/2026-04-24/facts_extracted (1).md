# Facts extracted from the two uploaded papers

This file gathers factual claims and reported findings from:

- **Westerberg et al. (2025)**, *Hierarchical substrates of prediction in visual cortical spiking*.
- **Bastos et al. (2020)**, *Layer and rhythm specificity for predictive routing*.

The emphasis is on the topics you requested:

- oddballs
- prediction error
- pure-global oddballs / global oddballs
- local oddballs
- working memory
- inhibition
- feedforward and feedback connectivity
- feedforward and feedback functional connectivity
- ubiquity
- interneurons
- laminar cortex
- higher-order and lower-order sensory cortex

The list below is strictly framed as **paper-derived factual statements**, not as a general literature review.

---

# 1. Shared conceptual background across the two papers

1. Both papers are framed within the broader predictive-processing / predictive-coding literature.
2. Both papers treat prediction and prediction-error signaling as hierarchical processes that may differ across cortical layers, areas, and directions of interareal interaction.
3. Both papers distinguish **feedforward** and **feedback** pathways rather than treating cortical responses as a single undifferentiated signal.
4. Both papers argue that laminar resolution matters for adjudicating predictive-coding theories.
5. Both papers explicitly analyze or discuss how top-down predictions may alter bottom-up sensory processing.

---

# 2. Facts from Westerberg et al. (2025)

## 2.1 Task structure and oddball definitions

1. The task is a **no-report** visual global-local oddball paradigm designed to reduce motor and reward confounds.
2. Stimulus sequences contain **four items**, labeled P1 to P4.
3. The habituated sequence is `x-x-x-y` or the counterbalanced reverse `y-y-y-x`.
4. In the main block, the habituated sequence occurs on **80% of trials** and the global oddball sequence `x-x-x-x` occurs on **20% of trials**.
5. The paper defines **global oddballs (GO)** as the unpredictable deviant sequences that violate the learned full-sequence prior.
6. The paper defines **local oddballs (LO)** as the within-sequence change at the fourth item in the habituated sequence, and these become highly predictable after extensive habituation.
7. Control blocks use predictable alternation to provide comparison sequences for the same P4 stimulus position.
8. The principal neural contrast is `(P4-P3 in main block) - (P4-P3 in control block)`.
9. This contrast is intended to separate prediction-related effects from short-term adaptation.

## 2.2 Prediction error and predictive-processing hypotheses examined

10. The paper tests three prominent predictive-processing hypotheses.
11. Hypothesis 1 is that higher-order cortex generates predictions that feed back to lower-order cortex and are subtracted from sensory input.
12. Hypothesis 2 is that prediction errors then feed forward up the hierarchy.
13. Hypothesis 3 is that prediction-error computations are distributed or ubiquitous across multiple cortical levels.
14. The paper explicitly notes that prior fMRI, EEG/MEG, and LFP studies could not cleanly separate feedback modulation from local computation and feedforward output.

## 2.3 Local oddballs

15. After extensive habituation, local oddballs are **predictable**, not surprising, in this task.
16. Despite being predictable, local oddballs are robustly signaled.
17. Local oddball signaling is reported in **all recorded areas** and in **both species**.
18. Local oddball responses emerge **early** in processing.
19. Local oddball responses show a **feedforward progression** across the visual hierarchy.
20. In the first roughly 150 ms of processing, local oddballs show timing consistent with feedforward flow.
21. Local oddball responses are strong by magnitude in both mice and monkeys.
22. Local oddball signaling involves **more than 50% of all recorded neurons** by median across areas.
23. In mice, local oddball signaling increases with ascending cortical hierarchy.
24. In monkeys, local oddball response strength is strongest in area MT.
25. In V1 of both species, local oddball signaling is especially prominent in **L2/3**.
26. The paper argues that local oddball responses do **not** behave like classical prediction errors in most areas.
27. Specifically, local oddball responses generally do **not** scale with sequence deviance as expected from a prediction-error account.
28. V4 is noted as an exception to the general absence of deviance scaling.
29. In some areas, especially mouse V1, the opposite pattern occurs, with more predictable local oddballs producing stronger responses.
30. The authors interpret local oddball detection primarily as a **release from adaptation**, not as prediction error.
31. The paper states that local oddballs are unsurprising yet still engage widespread cortical activity.
32. This is used as evidence against strong predictive suppression of expected local oddballs.

## 2.4 Global oddballs / pure-global oddball logic

33. Global oddballs are the **unpredictable** sequence violations in the task.
34. They are designed to circumvent low-level adaptation better than local oddballs.
35. Global oddball responses are **not ubiquitous** across cortex.
36. Global oddball signaling is restricted to a few **higher-order** areas rather than early-to-mid sensory cortex.
37. In mice, significant global oddball signals are reported in LM, PM, and AM.
38. In monkeys, significant global oddball signals are reported in V3, MT, 8A, and PFC.
39. At the individual-unit level, global oddball encoding is sparse.
40. Median proportion of global-oddball signaling units is about **7% in mice** and **8% in monkeys** across areas.
41. The latency of global oddball signaling does **not** scale with hierarchy the way a feedforward sweep would predict.
42. The authors state that this contradicts the idea of broad feedforward prediction-error propagation.
43. Putative L2/3 pyramidal cells in mice do not show global oddball signaling.
44. Current source density in mouse L2/3 does not reveal reliable synaptic activation changes during global oddballs.
45. Monkey area V3 also lacks global oddball signaling in L2/3 spiking.
46. Monkey area MT shows some L2/3 involvement, but it occurs **later** than PFC, which argues against feedforward origin.
47. The paper interprets global oddball signaling as more consistent with **feedback** than feedforward processing.
48. In mice, global oddball signals appear only in **extragranular** feedback-associated layers.
49. In monkeys, global oddball signals in visual cortex also appear only in **extragranular** layers.
50. Lower-order cortex shows global oddball effects later than higher-order cortex.
51. This temporal ordering is interpreted as propagation from higher to lower areas.
52. The paper states that prediction errors for global oddballs follow a **feedback signature** rather than a feedforward signature.
53. The discussion states that predictive processing in this paradigm appears largely as a property of **higher-order cortex**.
54. The authors connect this to the longer intrinsic timescales of higher-order areas.
55. They propose that higher-order neurons may be better suited for representing sequence context and predictions over longer timescales.

## 2.5 Inhibition and interneurons

56. Several predictive-processing models predict subtractive inhibition for predictable stimuli.
57. The paper directly tests this with cell-type-specific optogenetics.
58. In mice, SST+ and PV+ interneurons are optotagged.
59. In monkeys, optogenetic targeting is restricted to inhibitory interneurons.
60. In both species, inhibitory populations respond to the stimulus sequence overall.
61. In both species, inhibitory populations increase spiking during P4 of local oddballs.
62. However, the paper reports **no significant population global-oddball response** in these inhibitory subpopulations.
63. The authors therefore find no evidence that these interneuron classes implement the hypothesized predictive subtraction for global oddballs.
64. The paper concludes that global oddballs do **not** arise from a release of inhibition in PV/SST or pan-inhibitory populations.
65. The authors suggest a more **excitatory feedback-driven** mechanism for global oddball modulation.

## 2.6 Feedforward / feedback connectivity and functional connectivity

66. The paper evaluates directional interactions with **Granger causality** on spiking time courses.
67. The Granger analysis is done in mice using one neuronal time series per area.
68. For local oddballs, the cortical hierarchy becomes more **feedforward-dominated** in both early and late post-oddball windows.
69. This feedforward pattern propagates from V1 to higher visual areas during local oddball processing.
70. For global oddballs, there is **no change** in feedforward-versus-feedback asymmetry relative to baseline.
71. The Granger analysis therefore fails to support feedforward error propagation for global oddballs.
72. Combined with the latency and laminar results, the connectivity findings support a **feedback** model for global oddball processing.

## 2.7 Ubiquity, laminar cortex, and higher vs lower order cortex

73. The paper explicitly argues **against the ubiquity** of prediction-error signaling in sensory cortex.
74. The authors state that global oddball signaling is sparse and higher-order biased, not broadly distributed.
75. Laminar resolution is central to the argument because predictive-coding theories assign distinct roles to superficial, granular, and deep layers.
76. The paper reports that local oddball signaling is strongest in superficial L2/3 in V1.
77. The paper reports that global oddball signaling is concentrated in feedback-recipient extragranular compartments.
78. Lower-order sensory cortex does not show the expected dominant superficial feedforward global-oddball signal.
79. Higher-order cortex, especially primate PFC, shows the clearest global-oddball responses.
80. The authors therefore place predictive-processing computations in this task closer to **higher-order cortex** than to early sensory cortex.

---

# 3. Facts from Bastos et al. (2020)

## 3.1 Task, predictability, and working memory

81. The task is a **delayed match-to-sample** task.
82. Monkeys must fixate, view a sample, hold it across a delay, and then saccade to the matching item.
83. The paper explicitly frames the task as involving **working memory** and top-down control.
84. Predictability is manipulated blockwise.
85. In **predictable blocks**, the same sample object repeats for 50 trials.
86. In **unpredictable blocks**, one of three sample objects is chosen randomly on each trial for 50 trials.
87. The paper states that animals are more accurate and slightly faster during predictable blocks.
88. Frontoparietal cortex is included because of its established role in top-down attention and working memory.
89. The authors also interpret some rhythmic and parietal effects as relevant to working-memory maintenance and updating.
90. Area 7A high-beta effects are discussed as potentially engaging working-memory update mechanisms for unpredicted information.
91. The paper places its interpretation in a framework where bottom-up processing, top-down processing, and working memory interact.

## 3.2 Spiking and prediction error

92. During the sample interval, spiking is greater for **unpredictable** than predictable stimuli in all recorded areas.
93. Single-neuron information about sample identity is also greater during unpredictable than predictable samples during sample presentation.
94. V4 carries more sample information than the other recorded areas during the sample interval.
95. In V4, the unpredictable-minus-predictable spiking effect is stronger in **superficial** than deep layers.
96. During the presample interval, predictable blocks carry information about the upcoming sample in all areas.
97. PFC carries more information about the upcoming sample than V4 during the presample interval.
98. Presample predictive information is stronger in **deep** layers than superficial layers.
99. These findings are interpreted as consistent with higher and deeper cortex contributing more strongly to prediction generation.
100. The paper treats enhanced spiking to unpredicted stimuli as a hallmark of **prediction error** or error-like signaling.
101. It argues that superficial layers preferentially process and feed forward unpredicted inputs.

## 3.3 Oscillations, inhibition, and laminar cortex

102. During sample processing, **gamma power** is higher for unpredictable than predictable stimuli in all areas.
103. In all areas except FEF, **theta power** is also higher for unpredictable than predictable stimuli.
104. In general, **alpha** and **beta** power are higher for predictable than unpredictable stimuli.
105. Area **7A** is an exception, showing increased high-beta power for unpredictable stimuli.
106. V4 and PFC show larger superficial-than-deep gamma increases for unpredictable stimuli.
107. V4 also shows stronger superficial-than-deep theta increases for unpredictable stimuli.
108. In PFC, alpha and beta modulation related to predictability is stronger in superficial than deep layers during the sample interval.
109. In V4, deep-layer alpha increases for predictable samples, whereas superficial-layer alpha increases for unpredictable samples.
110. Sites with strong MUA modulation also tend to show strong gamma-power modulation.
111. In V4, alpha and beta power are negatively related to MUA modulation, especially in deep layers.
112. The paper repeatedly treats **alpha/beta** as inhibitory or gating rhythms that prepare sensory pathways for predicted input.
113. It explicitly proposes that alpha/beta rhythms inhibit gamma and spiking in pathways carrying predicted stimuli.
114. It states that top-down alpha/beta help regulate bottom-up processing served by gamma and spiking.
115. It places gamma predominantly in superficial feedforward cortex and alpha/beta predominantly in deep feedback cortex.
116. The discussion proposes that deep-layer alpha/beta can functionally inhibit superficial-layer gamma/spiking.

## 3.4 Feedforward and feedback connectivity / functional connectivity

117. The paper analyzes both **coherence** and **Granger causality** as measures of functional interaction.
118. During the sample interval, gamma-band coherence is higher for **unpredictable** than predictable stimuli.
119. The increase in gamma-band coherence for unpredictable stimuli is stronger in the **feedforward** than feedback direction.
120. In V4, feedforward GC enhancement during unpredictable samples is stronger in **superficial** layers than deep layers.
121. During predictable samples, alpha/beta coherence is greater overall.
122. The strongest predictable greater-than-unpredictable coherence effects involve **PFC**.
123. Predictable greater-than-unpredictable GC effects are concentrated in **feedback** direction and in alpha/beta frequencies.
124. In the presample interval, enhanced GC during predictable blocks is strongest from **deep layers of PFC** to the rest of the network.
125. The paper therefore supports a model in which prediction-related signaling travels in **feedback alpha/beta** channels and unpredicted/error-related signaling travels in **feedforward gamma** channels.
126. Theta also shows stronger interactions for unpredictable stimuli and is discussed as an additional carrier of feedforward communication.
127. Both coherence and GC are treated as evidence for frequency-specific **functional connectivity**.
128. The paper explicitly distinguishes **feedforward functional connections** from **feedback functional connections** using assumed cortical hierarchy.

## 3.5 Inhibition of V4 by higher-order cortex

129. The paper tests whether higher-order cortical rhythms explain trial-by-trial variance in V4 spiking and gamma.
130. Beta power in higher-order areas except 7A negatively couples to both spikes and gamma in V4.
131. Alpha in LIP and deep PFC negatively couples to deep-layer V4 spiking.
132. Beta in LIP, FEF, and superficial PFC negatively couples to deep-layer V4 spiking.
133. Deep-layer V4 gamma is negatively coupled to superficial and deep PFC beta and to superficial PFC alpha.
134. These negative couplings are interpreted as **top-down inhibition** of V4.
135. The paper notes that this inhibitory effect on V4 spiking is found in **deep layers** of V4.
136. The authors propose that different layers may transmit top-down prediction signals versus bottom-up routing of unpredicted information.

## 3.6 Stimulus specificity

137. Predictability-related modulation is **stimulus specific**.
138. In V4, gamma and MUA modulation for unpredicted stimuli is stronger for the site's **preferred** stimulus.
139. This preference effect for gamma and spiking is most evident in **superficial layers**.
140. Alpha and beta modulation for predicted stimuli is stronger for the preferred stimulus in **deep layers**.
141. The paper emphasizes that oscillatory prediction effects are representationally specific, not just nonspecific state changes.
142. This stimulus specificity is a central element of the paper's predictive-routing model.

## 3.7 Predictive routing model and relation to prediction error

143. The paper proposes **predictive routing** as an alternative implementation-level account of predictive coding.
144. In this model, there are no specialized circuits that explicitly compute prediction error by subtracting prediction from input.
145. Instead, predictions act by **alpha/beta preparation** that inhibits the sensory pathways expected to process the predicted input.
146. Because predicted pathways are inhibited, they show less gamma and less spiking.
147. Unexpected inputs produce stronger gamma/spiking because their pathways were **not pre-inhibited**.
148. The paper therefore reframes prediction error as the feedforward passage of unprepared, noninhibited sensory activity.
149. The model is explicitly laminar: deep layers carry the predictive alpha/beta preparation, whereas superficial layers carry feedforward gamma/spiking.
150. The paper's summary states that predictive coding may stem from rhythmic interactions in which lower-frequency rhythms in deep layers signal predictions and inhibit superficial-layer gamma and spiking in matching sensory pathways.

---

# 4. Direct comparisons between the two papers

151. Bastos et al. supports a classical-looking feedforward error / feedback prediction picture, but with a **rhythmic predictive-routing implementation**.
152. Westerberg et al. challenges multiple standard predictive-processing claims in a different task regime.
153. In Bastos et al., unpredictable stimuli increase superficial-layer gamma/spiking and feedforward functional connectivity.
154. In Westerberg et al., the strongest local expected oddball responses are widespread and feedforward, while the more surprising global oddballs are sparse and feedback-like.
155. Bastos et al. interprets alpha/beta as inhibitory top-down preparation.
156. Westerberg et al. directly tests inhibitory interneuron accounts and finds little support for a subtractive inhibitory mechanism for global oddballs.
157. Bastos et al. emphasizes stimulus-specific pathway inhibition.
158. Westerberg et al. emphasizes that higher-order cortex and feedback-recipient layers dominate global oddball responses.
159. Bastos et al. uses a working-memory DMS task with block predictability.
160. Westerberg et al. uses a passive no-report sequence-learning oddball design.
161. Bastos et al. presents evidence consistent with prediction errors flowing feedforward in gamma and predictions flowing feedback in alpha/beta.
162. Westerberg et al. presents evidence that global-oddball prediction-error-like responses do not show the expected ubiquitous feedforward sensory-cortex signature.
163. Taken together, the two papers do not simply replicate each other; they constrain different levels of the predictive-processing story.

---

# 5. Condensed topic index

## Oddballs

- Westerberg et al. is explicitly an oddball paper, with local and global oddballs.
- Bastos et al. discusses oddballs in the conceptual background but does not use the same local/global oddball design.

## Prediction error

- Westerberg et al. tests whether global oddballs carry feedforward prediction error and largely argues against the standard account in this task.
- Bastos et al. finds signatures consistent with feedforward processing of unpredicted stimuli and interprets them within predictive routing.

## Pure-global oddballs / global oddballs

- Westerberg et al.: sparse, higher-order biased, feedback-like, non-ubiquitous.

## Local oddballs

- Westerberg et al.: predictable, widespread, strong, early, feedforward, likely release from adaptation rather than prediction error.

## Working memory

- Bastos et al.: central to task interpretation and to some parietal/PFC discussions.
- Westerberg et al.: not a central construct in the task design.

## Inhibition

- Bastos et al.: alpha/beta is treated as a functional inhibitory mechanism on sensory pathways.
- Westerberg et al.: direct inhibitory-interneuron tests fail to support the expected predictive subtraction for global oddballs.

## Feedforward / feedback connectivity

- Bastos et al.: feedforward gamma/theta for unpredicted stimuli; feedback alpha/beta for predicted stimuli.
- Westerberg et al.: local oddballs show feedforward GC; global oddballs do not.

## Functional connectivity

- Bastos et al.: coherence and GC used explicitly as functional-connectivity analyses.
- Westerberg et al.: Granger causality used on area-level spiking time series.

## Ubiquity

- Westerberg et al.: argues against ubiquity of global-oddball prediction-error signaling in sensory cortex.

## Interneurons

- Westerberg et al.: PV, SST, and monkey inhibitory populations do not show the predicted global-oddball subtractive role.

## Laminar cortex

- Both papers treat laminar organization as crucial.
- Bastos et al.: deep alpha/beta and superficial gamma/spiking are central to predictive routing.
- Westerberg et al.: local oddballs prominent in L2/3; global oddballs concentrated in extragranular feedback-recipient layers.

## Higher-order vs lower-order sensory cortex

- Bastos et al.: higher-order cortex, especially PFC, is heavily involved in predictive feedback.
- Westerberg et al.: higher-order cortex is where global-oddball predictive-processing signals are most evident.

