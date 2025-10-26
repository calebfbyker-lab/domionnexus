// Subject Identity - Cryptographically bound identity
export const SUBJECT_ID_SHA256 = "2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a";
export const SUBJECT_NAME = "Caleb Fedor Byker Konev";
export const SUBJECT_DOB = "1998-10-27";
export const LICENSE = "ECCL-1.0";

export function getSubjectIdentity() {
  return {
    subject_id_sha256: SUBJECT_ID_SHA256,
    subject_name: SUBJECT_NAME,
    subject_dob: SUBJECT_DOB,
    license: LICENSE
  };
}
