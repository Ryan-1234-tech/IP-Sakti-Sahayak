"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

export type Jurisdiction = "INDIA" | "INTERNATIONAL";

interface JurisdictionContextType {
  jurisdiction: Jurisdiction;
  setJurisdiction: (j: Jurisdiction) => void;
  toggleJurisdiction: () => void;
}

const JurisdictionContext = createContext<JurisdictionContextType>({
  jurisdiction: "INDIA",
  setJurisdiction: () => {},
  toggleJurisdiction: () => {},
});

export function JurisdictionProvider({ children }: { children: React.ReactNode }) {
  const [jurisdiction, setJurisdictionState] = useState<Jurisdiction>("INDIA");

  useEffect(() => {
    try {
      const stored = localStorage.getItem("ipsakti_jurisdiction");
      if (stored === "INDIA" || stored === "INTERNATIONAL") {
        setJurisdictionState(stored);
      }
    } catch {
      // ignore
    }
  }, []);

  const setJurisdiction = (j: Jurisdiction) => {
    setJurisdictionState(j);
    try {
      localStorage.setItem("ipsakti_jurisdiction", j);
    } catch {
      // ignore
    }
  };

  const toggleJurisdiction = () => {
    setJurisdiction(jurisdiction === "INDIA" ? "INTERNATIONAL" : "INDIA");
  };

  return (
    <JurisdictionContext.Provider value={{ jurisdiction, setJurisdiction, toggleJurisdiction }}>
      {children}
    </JurisdictionContext.Provider>
  );
}

export function useJurisdiction() {
  return useContext(JurisdictionContext);
}
