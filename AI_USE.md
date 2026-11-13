#Disclosure of Artificial Intelligence (AI) Use

In accordance with the Space Apps 2026 guidelines, our team utilized Generative AI throughout the hackathon in the following specific capacities:

1. Strategic Research & Constraint Definition: AI (Claude and Gemini) was used as a rapid research assistant to isolate specific physical hardware constraints (e.g., VIPER 15° mobility limits, 110K cryogenic volatile phase thresholds) to define the mathematical boundaries for our dynamic Gap Matrix.
2. Code Acceleration: AI (Gemini) assisted our engineering workflow by generating boilerplate code for the FastAPI bridge and optimizing Numba array operations for our terrain ray-casting scripts.
3. Strict Scientific Isolation: Generative AI was strictly excluded from generating final data outputs, rankings, or physics calculations. All solar geometry, physical similarity scores, and multi-planetary matching metrics are calculated locally by our Python engine using true NAIF SPICE kernels and authentic NASA DEMs. No AI hallucination is present in the platform's analytical results.
