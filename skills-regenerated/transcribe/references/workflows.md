# Transcription Workflows

## Single File -- Fast Text

The simplest workflow: one audio file to plain text.

```bash
python3 transcribe_diarize.py recording.mp3 --out recording.txt
```

## Single File -- Structured JSON

Get timestamps and metadata in JSON format.

```bash
python3 transcribe_diarize.py recording.mp3 --response-format json --out recording.json
```

## Interview with Diarization

Transcribe with speaker identification. Provide known speaker references for labeled output.

```bash
python3 transcribe_diarize.py interview.m4a \
  --model gpt-4o-transcribe-diarize \
  --response-format diarized_json \
  --known-speaker "Alice=refs/alice.wav" \
  --known-speaker "Bob=refs/bob.wav" \
  --out-dir output/transcribe/interview
```

## Batch Transcription

Process multiple files with shared settings. Each file produces its own output.

```bash
python3 transcribe_diarize.py file1.mp3 file2.mp3 file3.mp3 \
  --out-dir output/transcribe/batch
```

## Non-English Audio

Add a language hint for improved accuracy.

```bash
python3 transcribe_diarize.py spanish_audio.mp3 --language es --out spanish.txt
```

## Dry Run -- Validate Without API Call

Preview the API payload without spending tokens.

```bash
python3 transcribe_diarize.py audio.wav --dry-run
```

## Output to stdout

Print the transcript directly instead of writing to a file.

```bash
python3 transcribe_diarize.py audio.wav --stdout
```
