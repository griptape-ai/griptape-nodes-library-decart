# Decart AI - Griptape Nodes Library

A comprehensive Griptape Nodes library for AI-powered content generation using the [Decart API](https://decart.ai/). Generate and transform images and videos with cutting-edge AI models through natural language prompts.

## 🎥 Features

### Lucy Dev Models
- **Image-to-Video (I2V)**: Convert static images into dynamic videos
- **Video-to-Video (V2V)**: Transform and edit existing videos

### Lucy Pro Models  
- **Text-to-Image (T2I)**: Generate high-quality images from text descriptions
- **Text-to-Video (T2V)**: Create videos directly from text prompts
- **Image-to-Video (I2V)**: Advanced image-to-video conversion with Pro quality
- **Image-to-Image (I2I)**: Transform and enhance existing images

### Technical Features
- **Multiple Input Formats**: Supports various artifact types and dictionary inputs
- **Seamless Integration**: Works within the Griptape Nodes ecosystem
- **Comprehensive Logging**: Built-in logging for debugging and monitoring
- **Error Handling**: Robust error handling with detailed feedback
- **Flexible Parameters**: Configurable seed, resolution, and prompt options

## 📦 Installation

### Prerequisites

- [Griptape Nodes](https://github.com/griptape-ai/griptape-nodes) installed and running
- Decart API key

### Install the Library on the machine where your Griptape Nodes Engine is running

1. **Download the library files** to your Griptape Nodes libraries directory:
   ```bash
   # Navigate to your Griptape Nodes libraries directory
   cd `gtn config show workspace_directory`
   
   # Clone or download this library
   git clone https://github.com/your-username/griptape-nodes-library-decart.git
   ```

2. In the Griptape Nodes Editor, add the libary by following these steps.
 * Open the Settings menu and navigate to the *Libaries* settings
 * Click on *+ Add Library* at the bottom of the settings panel
 * Enter the path to the library JSON file. This will be **your Griptape Nodes Workspace directory**`/griptape-nodes-library-decart/decart/griptape_nodes_library.json`. Remember you can check your Griptape Nodes Workspace directory with `gtn config show workspace_directory`
 * Close the Settings Panel
 * Click on *Refresh Libraries*


3. **Verify installation** by checking that all Decart nodes appear in your Griptape Nodes interface:
   - **Video/Decart category**: Lucy Dev I2V, Lucy Dev V2V, Lucy Pro T2V, Lucy Pro I2V, Lucy Video Edit
   - **Image/Decart category**: Lucy Pro T2I, Lucy Pro I2I

## 🔑 API Key Setup

### 1. Get Your Decart API Key

1. Visit [Decart.ai](https://decart.ai/)
2. Sign up for an account or log in
3. Navigate to the Use API section (currently bottom right of the page)
4. Your API key will be displayed in the modal panel

### 2. Configure the API Key

Set up your Decart API key in Griptape Nodes:

#### Option A: Griptape Nodes Configuration

The node will automatically look for the API key in the Griptape Nodes configuration under:
- **Key Name**: `"DECART_API_KEY"`

You can configure this through the Griptape Nodes settings interface. Open the *Settings* menu and navigate to *API Keys & Secrets* and click on *+ Add Secret* to add a new secret.

#### Option B: Environment Variable (Recommended)

```bash
export DECART_API_KEY="your-api-key-here"
```

Then restart Griptape Nodes to pick up the environment variable.


## 🚀 Usage

### Available Nodes

#### Lucy Dev Models
- **Decart Lucy Dev I2V**: Convert images to videos with development-quality processing
- **Decart Lucy Dev V2V**: Transform videos with development-quality processing

#### Lucy Pro Models
- **Decart Lucy Pro T2I**: Generate high-quality images from text prompts
- **Decart Lucy Pro T2V**: Create high-quality videos from text prompts  
- **Decart Lucy Pro I2V**: Convert images to videos with professional-quality processing
- **Decart Lucy Pro I2I**: Transform images with professional-quality processing

#### Legacy Node
- **Decart Lucy Video Edit**: Original video editing node (V2V functionality)

### Using in Griptape Nodes

1. **Add nodes** to your workflow by dragging from the appropriate category:
   - **Video/Decart**: For video generation and transformation nodes
   - **Image/Decart**: For image generation and transformation nodes
2. **Connect inputs** based on the node type:
   - Text-only nodes (T2I, T2V): Only require prompt input
   - Image input nodes (I2V, I2I): Require image input + prompt
   - Video input nodes (V2V): Require video input + prompt
3. **Configure parameters**: Set prompt, seed (optional), and resolution (optional)
4. **Connect outputs** to other nodes in your workflow
5. **Run your workflow** to generate content

### Supported Input Formats

- **Images**: ImageUrlArtifact, ImageArtifact, or dictionary representations
- **Videos**: VideoUrlArtifact, VideoArtifact, or dictionary representations  

### Example Prompts

#### Image Generation (T2I)
- `"A serene mountain landscape at sunset with golden light"`
- `"Portrait of a cyberpunk character with neon lighting"`
- `"Abstract geometric patterns in vibrant colors"`

#### Video Generation (T2V, I2V)
- `"A time-lapse of clouds moving across the sky"`
- `"Camera slowly zooming into a bustling city street"`
- `"Gentle waves lapping on a tropical beach"`

#### Image/Video Transformation (I2I, V2V)
- `"Change the background to a sunset scene"`
- `"Make the person wear a black leather jacket"`
- `"Add rain effects to the scene"`
- `"Convert to black and white with vintage film grain"`

## 📋 Node Parameters

### Common Parameters (All Nodes)

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `prompt` | string | Natural language description for generation/transformation | ✅ |
| `seed` | integer | Seed for reproducible generation | ❌ |
| `resolution` | string | Output resolution (default: "720p") | ❌ |

### Node-Specific Input Parameters

| Node Type | Additional Input | Type | Description |
|-----------|------------------|------|-------------|
| **T2I, T2V** | None | - | Text-only generation |
| **I2V, I2I** | `image_input` | ImageUrlArtifact, ImageArtifact | Source image |
| **V2V, Video Edit** | `video_input` | VideoUrlArtifact, VideoArtifact | Source video |

### Output Parameters

| Node Type | Output | Type | Description |
|-----------|--------|------|-------------|
| **T2I, I2I** | `image_output` | ImageUrlArtifact | Generated/transformed image |
| **T2V, I2V, V2V, Video Edit** | `video_output` | VideoUrlArtifact | Generated/transformed video |

## 🔧 Configuration

### API Configuration

All nodes use the following shared configuration:

- **Service Name**: `"Decart"`
- **API Key Environment Variable**: `"DECART_API_KEY"`
- **Base URL**: `"https://api.decart.ai/v1/generate/"`

### API Endpoints by Node

| Node | API Endpoint |
|------|--------------|
| **Lucy Dev I2V** | `lucy-dev-i2v` |
| **Lucy Dev V2V** | `lucy-dev-v2v` |
| **Lucy Pro T2I** | `lucy-pro-t2i` |
| **Lucy Pro T2V** | `lucy-pro-t2v` |
| **Lucy Pro I2V** | `lucy-pro-i2v` |
| **Lucy Pro I2I** | `lucy-pro-i2i` |
| **Lucy Video Edit** | `lucy-pro-v2v` |

## 📊 Logging

All nodes provide comprehensive API request logging for monitoring and debugging:

- Request URLs and parameters
- Response status codes and sizes  
- Error messages and stack traces
- Processing times and performance metrics

## 🛠️ Library Structure

```
griptape-nodes-library-decart/
├── decart/
│   ├── decart_lucy_dev_i2v.py       # Lucy Dev I2V node
│   ├── decart_lucy_dev_v2v.py       # Lucy Dev V2V node  
│   ├── decart_lucy_pro_t2i.py       # Lucy Pro T2I node
│   ├── decart_lucy_pro_t2v.py       # Lucy Pro T2V node
│   ├── decart_lucy_pro_i2v.py       # Lucy Pro I2V node
│   ├── decart_lucy_pro_i2i.py       # Lucy Pro I2I node
│   ├── decart_lucy_video_edit.py    # Legacy video edit node
│   └── griptape_nodes_library.json  # Library metadata and configuration
├── pyproject.toml                   # Package configuration
└── README.md                        # This documentation
```

### Node Metadata

The library includes a `griptape_nodes_library.json` file that defines:
- **7 total nodes** across Lucy Dev, Lucy Pro, and legacy models
- **Two categories**: Video/Decart and Image/Decart for organized node palette
- **API key configuration** requirements for DECART_API_KEY
- **Node descriptions and metadata** for each generation type

## 🔍 Troubleshooting

### Common Issues

#### API Key Not Found
```
ValueError: DecartLucyVideoEdit_1 is missing DECART_API_KEY. Ensure it's set in the environment/config.
```

**Solution**: Ensure your API key is properly configured using one of the methods described in the [API Key Setup](#-api-key-setup) section.

#### Invalid Input Format
```
ValueError: Unsupported image/video input type: <class 'str'>
```

**Solution**: Ensure your inputs are in supported formats:
- **Images**: ImageUrlArtifact, ImageArtifact, or dict
- **Videos**: VideoUrlArtifact, VideoArtifact, or dict
- **Flow**: File path, URL, or base64 string

#### API Request Failed
```
ERROR: Decart API request failed: 401 Client Error: Unauthorized
```

**Solution**: Check that your API key is valid and has sufficient credits/permissions.

### Debug Mode

Check the Griptape Nodes logs for information about the node execution. The node provides logging for all API interactions.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request for improvements to this Griptape Nodes library.

### Development

1. Fork the repository
2. Make your changes to the node implementation
3. Test the node within Griptape Nodes
4. Submit a Pull Request with your improvements

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/griptape-nodes-library-decart/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/griptape-nodes-library-decart/discussions)
- **Griptape Community**: [Griptape Discord](https://discord.gg/griptape)

## 🔗 Related Projects

- [Griptape Framework](https://github.com/griptape-ai/griptape)
- [Griptape Nodes](https://github.com/griptape-ai/griptape-nodes)
- [Griptape Nodes Directory](https://github.com/griptape-ai/griptape-nodes-directory)

---

Made with ❤️ for the Griptape community
