SUBJECT = "caleb fedor byker konev|1998-10-27"
def subject_fingerprint():
    import hashlib
    return hashlib.sha256(SUBJECT.encode()).hexdigest()
