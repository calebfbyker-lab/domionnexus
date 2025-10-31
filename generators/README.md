# Generators

This directory contains Python generator scripts and JSON schemas created during development chat sessions. These files were used to explore and design automation systems for the Domion Nexus project.

## Files

### Generator Scripts

These are Python scripts that generate complete repository structures with automation workflows:

- **`codex_automation_v3_generator.py`** - Generates v3 automation with Enochian, Hermetic, Kabbalistic modules, CNI (Celestial Neural Interface), and orchestration engine
- **`codex_automation_v4_generator.py`** - Generates v4 automation similar to v3 (appears to be an iteration)
- **`domionnexus_v2_generator.py`** - Generates v2 automation with reflective intelligence, curiosity reports, and adaptive provenance

### JSON Schemas

These define the structure for AstroCryptoSeal artifacts:

- **`astrocrypto_seal_schema_v4.json`** - JSON schema for v4.0 seals with sigils, glyphs, astro data, and provenance
- **`astrocrypto_seal_schema_v5.json`** - JSON schema for v5.0 seals (evolution of v4)

## Usage

### Running Generator Scripts

The generator scripts are designed to create complete directory structures with multiple files. They write to `/mnt/data/` paths by default:

```bash
# Example: Run the v3 generator
python3 generators/codex_automation_v3_generator.py
```

**Note:** You may need to modify the `BASE` path in each script to control where files are generated.

### Using JSON Schemas

The JSON schemas can be used to validate seal artifacts:

```bash
# Example: Validate a seal against the schema
# (Requires a JSON schema validator)
```

## Integration Status

These files represent design iterations from chat sessions. The actual implementation in this repository follows the Netlify-based architecture described in the main README.md, using:
- Node.js/JavaScript for build scripts
- Netlify Functions for serverless APIs
- React/Three.js for UI components

The Python generators were exploratory and helped define the conceptual structure that has been adapted for the web-based implementation.

## Binding

All automation concepts are bound to:
- **Subject:** CFBK (10/27/1998)
- **Subject SHA256:** `2948fbc4ba1c0d7341204908882b89134a999f3e8f77f4a6a00ce6b68770282a`

This ensures cryptographic traceability and provenance for all artifacts.
