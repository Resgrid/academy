"""Render each approved deep lesson in sequence, preserving validation state."""
import argparse, subprocess, sys
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument('--ffmpeg',required=True);p.add_argument('lessons',nargs='+');args=p.parse_args()
    script=Path(__file__).with_name('deep_dive.py')
    for ident in args.lessons:
        print('Rendering '+ident,flush=True)
        subprocess.run([sys.executable,str(script),'--render',ident,'--ffmpeg',args.ffmpeg],check=True)
if __name__=='__main__':main()
