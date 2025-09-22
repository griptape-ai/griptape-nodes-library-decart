# Decart Lucy Video Edit - Griptape Nodes Library

A Griptape Nodes library for video editing using the [Decart Lucy Video Edit API](https://decart.ai/). Transform and edit videos with AI-powered capabilities through natural language prompts.

## 🎥 Features

- **AI-Powered Video Editing**: Edit videos using natural language prompts
- **Multiple Input Formats**: Supports VideoUrlArtifact, VideoArtifact, and dictionary inputs
- **Seamless Integration**: Works within the Griptape Nodes ecosystem
- **Comprehensive Logging**: Built-in logging for debugging and monitoring
- **Error Handling**: Robust error handling with detailed feedback

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


3. **Verify installation** by checking that the "Decart Lucy Video Edit" node appears in your Griptape Nodes interface in the "Video/Decart" category.

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

### Using in Griptape Nodes

1. **Add the node** to your workflow by dragging "Decart Lucy Video Edit" from the node palette
2. **Connect your video input** to the `video_input` parameter
3. **Set your edit prompt** in the `prompt` parameter
4. **Connect the output** `video_output` to other nodes in your workflow
5. **Run your workflow** to process the video

### Supported Input Formats

The node accepts video inputs in multiple formats:

- **VideoUrlArtifact**: URLs pointing to video files
- **VideoArtifact**: Direct video file artifacts

### Example Prompts

- `"Change the background to a sunset scene"`
- `"Make the person wear a black leather jacket"`
- `"Add rain effects to the scene"`
- `"Convert to black and white with vintage film grain"`
- `"Remove the background and make it transparent"`

## 📋 Node Parameters

### Input Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `video_input` | VideoUrlArtifact, VideoArtifact, or dict | The input video to edit | ✅ |
| `prompt` | string | Natural language description of the desired edit | ✅ |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `video_output` | VideoUrlArtifact | The edited video result |

## 🔧 Configuration

### API Configuration

The node uses the following configuration:

- **Service Name**: `"Decart"`
- **API Key Environment Variable**: `"DECART_API_KEY"`
- **Base URL**: `"https://api.decart.ai/v1/generate/"`
- **Model**: `"lucy-pro-v2v"`

## 📊 Logging

The node provides API request logging for monitoring and debugging:

## 🛠️ Library Structure

```
griptape-nodes-library-decart/
├── decart/
│   ├── decart_lucy_video_edit.py    # Main node implementation
│   └── griptape_nodes_library.json  # Node metadata and configuration
├── pyproject.toml                   # Package configuration
└── README.md                        # This documentation
```

### Node Metadata

The library includes a `griptape_nodes_library.json` file that defines:
- Node categories and display information
- API key configuration requirements
- Node descriptions and metadata

## 🔍 Troubleshooting

### Common Issues

#### API Key Not Found
```
ValueError: DecartLucyVideoEdit_1 is missing DECART_API_KEY. Ensure it's set in the environment/config.
```

**Solution**: Ensure your API key is properly configured using one of the methods described in the [API Key Setup](#-api-key-setup) section.

#### Invalid Video Format
```
ValueError: Unsupported video input type: <class 'str'>
```

**Solution**: Ensure your video input is in one of the supported formats (VideoUrlArtifact, VideoArtifact).

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
