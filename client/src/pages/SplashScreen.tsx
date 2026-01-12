import { useEffect } from "react";
import logo from "../assets/auto-decode-logo.png";
import "./SplashScreen.css";

const words = [
  "jeje",
  "lodi",
  "petmalu",
  "werpa",
  "awit",
  "charot",
  "sanaol",
  "g",
  "kklk",
  "omsim",
  "lods",
  "sheesh",
  "gets",
  "wala",
  "grabe",
  "skt",
  "yolo",
  "fomo",
  "tbh",
  "btw",
  "idk",
  "brb",
  "smh",
  "ikr",
  "tgif",
];

export default function SplashScreen({ onFinish }: { onFinish: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onFinish, 3000);
    return () => clearTimeout(timer);
  }, [onFinish]);

  return (
    <div className="splash-container">
      {/* Floating words */}
      {words.map((word, i) => (
        <span
          key={i}
          className="floating-word"
          style={{
            left: `${Math.random() * 90}%`,
            top: `${Math.random() * 90}%`,
            animationDelay: `${Math.random() * 3}s`,
          }}
        >
          {word}
        </span>
      ))}

      {/* Logo */}
      <img
        src={logo}
        alt="Group 12's AutoDecode Logo"
        className="splash-logo"
      />

      <h3 className="splash-tagline">Analyzing Filipino Netspeak: Finite Automata for Taglish Obfuscation Detection</h3>
      <p className="group-credit">Group 12 - BSCS 3-1</p>
    </div>
  );
}
