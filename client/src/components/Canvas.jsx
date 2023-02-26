import React, { useState, useRef } from "react";
import { Flex, Box, Button, Textarea } from "@chakra-ui/react";

const Canvas = () => {
  const [image, setImage] = useState(null);
  const [text, setText] = useState("");
  const canvasRef = useRef(null);

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    const reader = new FileReader();
    reader.onload = () => {
      const img = new Image();
      img.onload = () => {
        const canvas = canvasRef.current;
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);
        setImage(canvas.toDataURL());
      };
      img.src = reader.result;
    };
    reader.readAsDataURL(file);
  };

  const handleTextChange = (event) => {
    setText(event.target.value);
  };

  const handleAddText = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.font = "30px Arial";
    ctx.fillStyle = "#000000";
    ctx.fillText(text, 50, 50);
    setText("");
  };

  return (
    <Flex alignItems="center" justifyContent="center" h="100vh">
      <Box
        bg="gray.100"
        p={10}
        w="70%"
        h="70%"
        border="2px dashed"
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
      >
        <canvas ref={canvasRef} />
        {image && <img src={image} alt="Uploaded" />}
        <Textarea
          mt={5}
          value={text}
          onChange={handleTextChange}
          placeholder="Type something here"
        />
        <Button mt={2} onClick={handleAddText}>
          Add Text
        </Button>
      </Box>
    </Flex>
  );
};

export default Canvas;