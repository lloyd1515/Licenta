// a2: placeholder stage; a HyperFrames clip is laid over these scenes by stitch.py.
Kit.module("a2", (K) => {
  K.scene("a2-envelope", () => {
    K.heading("a2-envelope", { at: "a2-envelope|Each Wi-Fi message" });
  });
  K.scene("a2-arrow", () => {
    K.heading("a2-arrow", { at: "a2-arrow|Why two numbers" });
  });
  K.scene("a2-eq", () => {
    K.heading("a2-eq", { at: "a2-eq|Next" });
  });
  K.scene("a2-alarm", () => {
    K.heading("a2-alarm", { at: "a2-alarm|But a jerk" });
  });
});
