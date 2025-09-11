# Doctor Whitelist Generator

This script generates a `doctor_whitelist.json` file with authorized doctor IDs for the Medical Deepfake Labeling Application.

## Features

- 🎲 **Random ID Generation**: Generate random doctor IDs with customizable patterns
- 📝 **Interactive Mode**: Manually enter doctor IDs one by one
- 📁 **File Import**: Import doctor IDs from text files or CSV files
- 🔄 **Batch Processing**: Combine multiple sources in one operation
- ✅ **Validation**: Automatic duplicate detection and validation
- 📊 **Flexible Output**: Customizable output file names

## Usage

### Basic Commands

```bash
# Show help
python generate_doctor_whitelist.py --help

# Interactive mode (manually enter IDs)
python generate_doctor_whitelist.py --interactive

# Generate 10 random IDs
python generate_doctor_whitelist.py --random 10

# Generate IDs with custom pattern
python generate_doctor_whitelist.py --random 5 --pattern "MD{number}"

# Import from text file
python generate_doctor_whitelist.py --from-file doctors.txt

# Import from CSV file
python generate_doctor_whitelist.py --from-csv doctors.csv

# Display the generated whitelist
python generate_doctor_whitelist.py --random 5 --show
```

### Advanced Usage

```bash
# Combine multiple sources
python generate_doctor_whitelist.py --random 5 --from-file doctors.txt --from-csv doctors.csv

# Custom output file
python generate_doctor_whitelist.py --random 10 --output custom_whitelist.json

# Custom pattern with multiple placeholders
python generate_doctor_whitelist.py --random 5 --pattern "HOSP_{letter}_{number}"
```

## Pattern Options

The `--pattern` option supports several placeholders:

- `{number}`: Random 4-digit number (1000-9999)
- `{random}`: Random 4-character alphanumeric string
- `{letter}`: Random uppercase letter

### Pattern Examples

```bash
# Default pattern
DOC{number}          # Results: DOC1234, DOC5678, etc.

# Medical department pattern
MD{number}           # Results: MD1234, MD5678, etc.

# Hospital code pattern
HOSP_{letter}_{number}  # Results: HOSP_A_1234, HOSP_B_5678, etc.

# Random alphanumeric pattern
DOC_{random}         # Results: DOC_A1B2, DOC_C3D4, etc.
```

## Input File Formats

### Text File Format

Create a text file with one doctor ID per line:

```
DR001
DR002
DR003
MD_ALICE
MD_BOB
DOC_SMITH
```

### CSV File Format

Create a CSV file with doctor IDs in the first column:

```csv
Doctor_ID,Name,Department,Email
DR001,Dr. Alice Johnson,Cardiology,alice.johnson@hospital.com
DR002,Dr. Bob Smith,Neurology,bob.smith@hospital.com
DR003,Dr. Charlie Brown,Oncology,charlie.brown@hospital.com
```

## Output Format

The script generates a `doctor_whitelist.json` file with the following structure:

```json
{
  "created": "2024-01-01T12:00:00.000000",
  "total_doctors": 15,
  "whitelist": [
    "DOC1017",
    "DOC5919",
    "DOC8029",
    "DOC8078",
    "DOC9476",
    "DOC_JONES",
    "DOC_SMITH",
    "DR001",
    "DR002",
    "DR003",
    "DR004",
    "DR005",
    "MD_ALICE",
    "MD_BOB",
    "MD_CHARLE"
  ]
}
```

## Security Features

- **Duplicate Prevention**: Automatically prevents duplicate doctor IDs
- **Case Sensitivity**: Doctor IDs are case-sensitive for security
- **Sorted Output**: IDs are sorted alphabetically for consistency
- **Validation**: Empty or invalid IDs are automatically filtered out

## Integration with Application

After generating the whitelist:

1. **Place the file**: Copy `doctor_whitelist.json` to your application directory
2. **View the whitelist**: Use `python show_doctor_ids.py` to display authorized IDs
3. **Distribute IDs**: Share the doctor IDs with authorized medical professionals
4. **Test access**: Verify that only whitelisted IDs can access the application

## Examples

### Example 1: Quick Setup for 20 Doctors

```bash
python generate_doctor_whitelist.py --random 20 --pattern "DOC{number}" --show
```

### Example 2: Import Existing Doctor List

```bash
python generate_doctor_whitelist.py --from-file existing_doctors.txt --output production_whitelist.json
```

### Example 3: Combine Random and Imported IDs

```bash
python generate_doctor_whitelist.py --random 10 --from-file department_heads.txt --show
```

### Example 4: Custom Hospital Pattern

```bash
python generate_doctor_whitelist.py --random 15 --pattern "HOSP_{letter}{number}" --show
```

## Troubleshooting

### Common Issues

1. **File not found**: Ensure input files exist and paths are correct
2. **Permission denied**: Check file permissions for reading input files and writing output
3. **Empty whitelist**: Verify input files contain valid doctor IDs
4. **Duplicate IDs**: The script automatically handles duplicates

### Validation

- Doctor IDs must be non-empty strings
- Duplicates are automatically removed
- IDs are trimmed of whitespace
- Case sensitivity is preserved

## Best Practices

1. **Backup**: Always backup existing whitelist files before regeneration
2. **Testing**: Test the whitelist with a small number of IDs first
3. **Documentation**: Keep track of which IDs are assigned to which doctors
4. **Security**: Store the whitelist file securely and limit access
5. **Version Control**: Consider versioning your whitelist files

## Sample Files

The repository includes sample files for testing:

- `sample_doctors.txt`: Sample text file with doctor IDs
- `sample_doctors.csv`: Sample CSV file with doctor information

Use these files to test the import functionality:

```bash
python generate_doctor_whitelist.py --from-file sample_doctors.txt --show
python generate_doctor_whitelist.py --from-csv sample_doctors.csv --show
```

## Support

For issues or questions about the whitelist generator, please contact the development team.
