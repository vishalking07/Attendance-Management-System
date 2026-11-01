// Helper for realistic, non-animated person portrait photos
export const REAL_PERSON_PORTRAITS = [
  "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200&auto=format&fit=crop&q=80", // Young man
  "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80", // Young smiling man
  "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80", // Man portrait
  "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&auto=format&fit=crop&q=80", // Young woman
  "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=200&auto=format&fit=crop&q=80", // Man casual
  "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80", // Professional woman
  "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&auto=format&fit=crop&q=80", // Man studio
  "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=200&auto=format&fit=crop&q=80", // Modern man
  "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=200&auto=format&fit=crop&q=80", // Woman student
  "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200&auto=format&fit=crop&q=80", // Young woman
];

export const getPersonPhoto = (name = '', fallbackIdx = 0) => {
  if (!name) return REAL_PERSON_PORTRAITS[fallbackIdx % REAL_PERSON_PORTRAITS.length];
  
  const lower = name.toLowerCase();
  if (lower.includes('vishal')) {
    return REAL_PERSON_PORTRAITS[0]; // Vishal
  }
  if (lower.includes('nithish')) {
    return REAL_PERSON_PORTRAITS[1]; // Nithishkumar
  }

  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = (hash + name.charCodeAt(i)) % REAL_PERSON_PORTRAITS.length;
  }
  return REAL_PERSON_PORTRAITS[hash];
};

export default getPersonPhoto;
