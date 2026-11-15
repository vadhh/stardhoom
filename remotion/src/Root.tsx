import React from "react";
import { Composition } from "remotion";
import { BatikHeroScene } from "./BatikHeroScene";
import { FooterBatikScene } from "./FooterBatikScene";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="BatikHeroLoop"
        component={BatikHeroScene}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          mode: "loop",
          bgColor: "#141414",
          inkColor: "#F2F2F2",
          stippleDensity: 1,
          maxIntensity: 0.82,
          showHeroOverlay: false,
        }}
      />
      <Composition
        id="BatikHeroWithOverlay"
        component={BatikHeroScene}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          mode: "loop",
          bgColor: "#141414",
          inkColor: "#F2F2F2",
          stippleDensity: 1,
          maxIntensity: 0.78,
          showHeroOverlay: true,
        }}
      />
      <Composition
        id="BatikHeroEntrance"
        component={BatikHeroScene}
        durationInFrames={360}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          mode: "entrance",
          bgColor: "#141414",
          inkColor: "#F2F2F2",
          stippleDensity: 1,
          maxIntensity: 0.82,
          showHeroOverlay: false,
        }}
      />
      {/* encoded to img/footer-batik-av1.mp4, .mp4 and .jpg (DESIGN.md, Building) for the screen that closes the site. No text sits on it there, so it
          runs at the hero's strength, 0.78 (with text on top, 0.55 kept #F2F2F2 at 5.1:1 over the brightest dots) */}
      <Composition
        id="FooterBatikLoop"
        component={FooterBatikScene}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ intensity: 0.78 }}
      />
    </>
  );
};
