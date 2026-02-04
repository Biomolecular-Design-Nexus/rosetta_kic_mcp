# Rosetta KIC MCP Server Test Prompts

## Tool Discovery Tests

### Prompt 1: List All Tools
"What MCP tools are available for cyclic peptides? Give me a brief description of each."

### Prompt 2: Tool Details
"Explain how to use the validate_peptide_sequence tool, including all parameters."

### Prompt 3: Server Information
"Get server information about the rosetta-kic-mcp server."

## Sync Tool Tests

### Prompt 4: Sequence Validation - Valid
"Validate the peptide sequence 'GRGDSP'"

### Prompt 5: Sequence Validation - Invalid
"Validate the peptide sequence 'GRGDXP' (contains invalid amino acid X)"

### Prompt 6: Structure Validation - Need File
"I have a PDB file with a cyclic peptide structure. How can I validate it?"

### Prompt 7: Error Handling
"Validate an empty peptide sequence ''"

## Submit API Tests

### Prompt 8: Submit Structure Prediction
"Submit a 3D structure prediction job for the peptide sequence 'GRGDSP' with 5 structures and 600 second runtime"

### Prompt 9: Check Job Status
"What's the status of job <job_id>?"

### Prompt 10: Get Results
"Show me the results of job <job_id>"

### Prompt 11: View Logs
"Show the last 30 lines of logs for job <job_id>"

### Prompt 12: List Jobs
"List all jobs with status 'completed'"

### Prompt 13: Cancel Job
"Cancel the job <job_id>"

## Submit Tools with File Input

### Prompt 14: Submit Cyclic Closure (Need File)
"I want to submit a cyclic peptide closure job. What input do I need?"

### Prompt 15: Submit Loop Modeling (Need File)
"Submit a loop modeling job to model residues 5-12 of a protein structure"

## Batch Processing Tests

### Prompt 16: Batch Structure Prediction
"Submit batch structure prediction for these sequences: 'GRGDSP', 'RGDFV', 'YIGSR' with 3 structures each"

### Prompt 17: Batch Results
"Get all results from batch job <batch_job_id>"

## Job Management Tests

### Prompt 18: List All Jobs
"List all submitted jobs regardless of status"

### Prompt 19: Clean Old Jobs
"Clean up completed jobs older than 30 days"

## Error Handling and Edge Cases

### Prompt 20: Invalid Sequence Characters
"Submit structure prediction for sequence 'ABCXYZ' (invalid amino acids)"

### Prompt 21: Empty Job List
"List jobs when no jobs have been submitted"

### Prompt 22: Non-existent Job
"Get status of job 'nonexistent123'"

## End-to-End Scenarios

### Prompt 23: Full Validation Workflow
"I have a peptide sequence 'GRGDSPK'. First validate it, then if valid, submit a structure prediction job."

### Prompt 24: Job Monitoring Workflow
"Submit a structure prediction for 'CYCLICPEP', then check its status every few seconds until complete."

### Prompt 25: Batch Analysis Workflow
"Validate these sequences first: 'GRGDSP', 'INVALID', 'RGDFV'. Then submit valid ones for structure prediction in batch."

## Expected Responses Guide

### Sync Tool Success Response Format:
```json
{
  "status": "success",
  "result": { ... actual results ... }
}
```

### Submit API Success Response Format:
```json
{
  "status": "submitted",
  "job_id": "abc12345",
  "message": "Job submitted. Use get_job_status('abc12345') to check progress."
}
```

### Error Response Format:
```json
{
  "status": "error",
  "error": "Description of the error",
  "error_type": "validation_error|runtime_error"
}
```

### Job Status Response Format:
```json
{
  "job_id": "abc12345",
  "status": "pending|running|completed|failed|cancelled",
  "submitted_at": "2024-01-01T12:00:00",
  "started_at": "2024-01-01T12:01:00",
  "completed_at": "2024-01-01T12:30:00"
}
```