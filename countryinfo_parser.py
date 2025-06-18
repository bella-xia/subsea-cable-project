import os, argparse



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, default='data/countryInfo.txt')
    args = parser.parse_args()

    if not args.input_dir or not os.path.exists(args.input_dir):
       raise Exception(f"unable to identify input data {args.input_dir}")

    with open(args.input_dir, 'r') as f:
        text = f.read()

    text_lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 2]
    print(f"there are a total of {len(text_lines)} lines")

    # goto the end of metadata
    idx = 0
    while text_lines[idx].startswith("# "):
        idx += 1
    
    header_line = text_lines[idx][1:]
    headers = [header for header in header_line.split('\t') if len(header) > 0]
    data = [inst for inst in text_lines[idx+1].split('\t')]
    for i in range(len(data)):
        print(f"{headers[i]}: {data[i]}")
    exit(0)
    for i in range(idx+1, idx+5): 
                   # len(text_lines)):
        data = [inst for inst in text_lines[i].split('\t')] 
                # if len(inst) > 0]
        print(len(data))
    

    
