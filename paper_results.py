"""Compatibility entry point for the synchronized publication pipeline.
The earlier screenshot-transcription generator is archived in archive/pre_sync.
Run: python paper_results.py
"""
from publication.build import main

if __name__ == '__main__':
    main()
