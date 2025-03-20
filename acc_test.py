import os
import subprocess
import random
from pathlib import Path
import difflib
import logging
from datetime import datetime

# logging
log_filename = f"data/shn_acc_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def test_checkpoint(checkpoint_path, image_path, gt_path):
    """Test a checkpoint against an image and ground truth file."""
    cmd = [
        'tesseract',
        image_path,
        'stdout',
        '--tessdata-dir', os.path.dirname(checkpoint_path),
        '-l', os.path.basename(checkpoint_path).replace('.traineddata', ''),
        '--psm', '6'
    ]
    
    try:
        # Run tesseract with the checkpoint
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        ocr_text = result.stdout.strip()
        
        # Read ground truth
        with open(gt_path, 'r', encoding='utf-8') as f:
            gt_text = f.read().strip()
        
        # Calculate similarity
        similarity = difflib.SequenceMatcher(None, ocr_text, gt_text).ratio() * 100
        
        # Log comparison
        logging.info(f"\nImage: {os.path.basename(image_path)}")
        logging.info(f"Checkpoint: {os.path.basename(checkpoint_path)}")
        logging.info(f"Similarity: {similarity:.2f}%")
        logging.info("-" * 50)
        # logging.info("Ground Truth:")
        # logging.info(gt_text)
        # logging.info("-" * 50)
        # logging.info("OCR Output:")
        # logging.info(ocr_text)
        # logging.info("=" * 50)
        
        return {
            'checkpoint': os.path.basename(checkpoint_path),
            'image': os.path.basename(image_path),
            'similarity': similarity,
            'ocr_text': ocr_text,
            'gt_text': gt_text
        }
    except subprocess.CalledProcessError as e:
        logging.error(f"Error testing {checkpoint_path} with {image_path}: {e}")
        return {
            'checkpoint': os.path.basename(checkpoint_path),
            'image': os.path.basename(image_path),
            'similarity': 0,
            'error': str(e)
        }

def main():
    # Paths
    checkpoints_dir = Path('data/shn/tessdata_best')
    test_images_dir = Path('data/shn-ground-truth')

    test_sample_length = 300
    
    # Find all checkpoint files
    checkpoints = list(checkpoints_dir.glob('*.traineddata'))
    if not checkpoints:
        logging.error(f"No checkpoint files found in {checkpoints_dir}")
        return
    
    # Find all test image files with corresponding ground truth files
    valid_test_pairs = []
    for image_path in test_images_dir.glob('*.tif'):
        gt_path = image_path.with_suffix('.gt.txt')
        if gt_path.exists():
            valid_test_pairs.append((image_path, gt_path))
    
    if not valid_test_pairs:
        logging.error(f"No valid test image and ground truth pairs found in {test_images_dir}")
        return
    
    # Shuffle and limit to 1000 examples
    random.seed(42)  # For reproducibility
    random.shuffle(valid_test_pairs)
    test_sample = valid_test_pairs[:min(test_sample_length, len(valid_test_pairs))]
    
    logging.info(f"Testing with {len(test_sample)} randomly selected image-ground truth pairs")
    
    # Store results for all checkpoints
    all_results = []
    
    # Test each checkpoint with the same set of images
    for checkpoint in checkpoints:
        logging.info(f"\nTesting checkpoint: {checkpoint.name}")
        checkpoint_results = []
        
        for image_path, gt_path in test_sample:
            result = test_checkpoint(str(checkpoint), str(image_path), str(gt_path))
            checkpoint_results.append(result)
            all_results.append(result)
        
        # Calculate average similarity for this checkpoint
        if checkpoint_results:
            avg_similarity = sum(r['similarity'] for r in checkpoint_results) / len(checkpoint_results)
            logging.info(f"  Average Similarity: {avg_similarity:.2f}%")
            logging.info("-" * 50)
    
    # Sort checkpoints by average similarity
    checkpoint_avg = {}
    for result in all_results:
        checkpoint = result['checkpoint']
        if checkpoint not in checkpoint_avg:
            checkpoint_avg[checkpoint] = {'similarity_sum': 0, 'count': 0}
        
        checkpoint_avg[checkpoint]['similarity_sum'] += result['similarity']
        checkpoint_avg[checkpoint]['count'] += 1
    
    # Calculate averages and sort
    for checkpoint in checkpoint_avg:
        count = checkpoint_avg[checkpoint]['count']
        checkpoint_avg[checkpoint]['avg_similarity'] = checkpoint_avg[checkpoint]['similarity_sum'] / count
    
    # Sort by average similarity
    sorted_checkpoints = sorted(
        checkpoint_avg.items(),
        key=lambda x: x[1]['avg_similarity'],
        reverse=True
    )
    
    # Print final sorted results
    logging.info("\nCheckpoints Ranked by Performance:")
    logging.info("=" * 70)
    for i, (checkpoint, stats) in enumerate(sorted_checkpoints, 1):
        logging.info(f"{i}. {checkpoint}")
        logging.info(f"   Average Similarity: {stats['avg_similarity']:.2f}%")
    
    # Print the best checkpoint
    if sorted_checkpoints:
        best_checkpoint = sorted_checkpoints[0][0]
        logging.info("\n" + "=" * 70)
        logging.info(f"Best Checkpoint: {best_checkpoint}")
        logging.info(f"Average Similarity: {sorted_checkpoints[0][1]['avg_similarity']:.2f}%")
        logging.info(f"Tested with {len(test_sample)} random samples")

if __name__ == "__main__":
    main()

