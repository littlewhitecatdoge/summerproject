import React, { Component } from "react";
import ReactDOM from "react-dom";
import axios from "axios";
import './App.css';

class App extends Component {
  state = {
    file: null,
    content: ""

  };
  
  handleFile(e) {
    let file = e.target.files[0];
    this.setState({ file });
  }

  async handleUpload(e) {
    console.log(this.state.file);
    const value=await uploadImage(this.state.file);
    this.setState(value)
  }

  render() {
    return (
      <div>
        <div className="title">Pneumothorax Detection</div>
        <div className="head">Images-Upload</div>
        <div className="content">
        <input type="file" className="file" name="file" onChange={e => this.handleFile(e)} />
        <button className="button" onClick={e => this.handleUpload(e)}>Detect</button>
        </div>
        <div className="head">Result-Get</div>
        <div className="content">
        <p className="p1">Result: {this.state.content}</p>
        </div>
      </div>
    );
  }
}

const uploadImage = async file => {
  try {
    console.log("Upload Image", file);
    const formData = new FormData();
    formData.append("filename", file);
    formData.append("destination", "images");
    formData.append("create_thumbnail", true);
    const config = {
      headers: {
        "content-type": "multipart/form-data"
      }
    };
    const API = "uploadphoto";
    const HOST = "http://localhost:5001";
    const url = `${HOST}/${API}`;

    const photo = await axios.post(url, formData, config).then(res=>res.data);
    console.log("uploadphoto: ", photo);
    return photo
  } catch (error) {
    console.error(error);
  }
  
};
const rootElement = document.getElementById("root");
ReactDOM.render(<App />, rootElement);

export default App;

