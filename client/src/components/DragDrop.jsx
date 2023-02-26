import { useState, useEffect } from 'react';
import { Box, Text, Spinner, Alert, AlertIcon, AlertTitle, VStack, Center, Heading, Button, Container, HStack, Wrap, WrapItem, Image, Stack, Flex, SimpleGrid,   Menu,
  MenuButton,
  MenuList,
  MenuItem, 
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon} from '@chakra-ui/react';
import { useDropzone } from 'react-dropzone';
import { FaFileUpload } from 'react-icons/fa';
import axios from 'axios';

function DragAndDrop() {
  const [uploadedFileTitles, setUploadedFileTiles] = useState([]);
  const [uploadedFileNames, setUploadedFileNames] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [selectedFileTitle, setSelectedFileTitle] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [summary, setSummary] = useState('');
  const [keyConcepts, setKeyConcepts] = useState('');
  const [highlights, setHighlights] = useState('');
  const [limitations, setLimitations] = useState('');
  const [authors, setAuthors] = useState('');

  const [tables, setTables] = useState([]);
  const [figures, setFigures] = useState([]);
  const [dropdowns, setDropdowns] = useState([false, false, false]);

  const toggleDropdown = (index) => {
    const updatedDropdowns = dropdowns.map((value, i) => i === index);
    setDropdowns(updatedDropdowns);
  };

  const [accordionState, setAccordionState] = useState({
    keyConcepts: false,
    highlights: false,
    summary: false,
    tables: false,
    figures: false,
    limitations: false,
    references: false,
    authors: false
  });

  const handleAccordionClick = (section) => {
    setAccordionState((prevState) => {
      const newState = {};
      Object.keys(prevState).forEach((key) => {
        if (key === section) {
          newState[key] = !prevState[key];
        } else {
          newState[key] = false;
        }
      });
      return newState;
    });
  };
  const handleDrop = (acceptedFiles) => {
    const formData = new FormData();
    formData.append('file', acceptedFiles[0]);
    setIsUploading(true);
    setLoadingSummary(false);
    setTimeout(() => {axios.post('http://localhost:4949/upload',
      formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        mode: 'cors',
      }
    ).then((response) => {
      if (response.status === 200) {
        const title = response.data.title;
        const tables = response.data.tables;
        const figures = response.data.figures;
        
        const authors = response.data.authors;
        const summary = response.data.summary;
        const key_concepts = response.data.key_concepts;
        const highlights = response.data.highlights;
        const limitations = response.data.limitations;
        
        console.log(response.data)
        setUploadedFileTiles([...uploadedFileTitles, title]);
        setUploadedFileNames([...uploadedFileNames, acceptedFiles[0].name]);
        setFigures(figures);
        setAuthors(authors);
        setTables(tables);
        setSummary(summary);
        setKeyConcepts(key_concepts);
        setHighlights(highlights);
        setLimitations(limitations);
      } else {
        alert('Failed to upload PDF file');
      }
      setIsUploading(false);
      setIsSuccess(true);
      setLoadingSummary(true);
    })
    .catch((error) => {
      console.error(error);
      alert('An error occurred while uploading the PDF file');
      setIsUploading(false);
    });
    }, 3000);
  };

  const handleItemClick = (fileTitleIndex) => {
    // TODO: send request to backend to get summary
    // TODO: display summary in the text area
    setSelectedFileTitle(uploadedFileTitles[fileTitleIndex]);
    setLoadingSummary(false);
    setTimeout(() => {
      axios.post('http://localhost:4949/handle_summary',
        {
          file_name: uploadedFileNames[fileTitleIndex]
        }
      ).then((response) => {
        if (response.status === 200) {
          const tables = response.data.tables;
          const figures = response.data.figures;
          const authors = response.data.authors;
          const key_concepts = response.data.key_concepts;
          const summary = response.data.summary;
          const highlights = response.data.highlights;
          const limitations = response.data.limitations;
          setSummary(summary);
          setAuthors(authors);
          setKeyConcepts(key_concepts);
          setHighlights(highlights);
          setLimitations(limitations);
          setFigures(figures);
          setTables(tables);
        } else {
          alert('Failed to get summary');
        }
        setLoadingSummary(true);
      })
      .catch((error) => {
        console.error(error);
        alert('An error occurred while getting the summary');
        setLoadingSummary(false);
      });
    }, 3000);
  }
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsSuccess(false);
    }, 2000);

    return () => {
      clearTimeout(timer);
    };
  }, [isSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop: handleDrop });

  return (
    <Flex gap='2' width={900}>
      {/* alignItems="center" justifyContent="center" */}
      <Box borderWidth="1px" borderRadius="lg" p="6" width={600}>
        <Accordion>
          <AccordionItem width="200">
            <AccordionButton onClick={() => handleAccordionClick("authors")} _expanded={{ bg: 'tomato', color: 'white' }}>
              <Box flex="1" textAlign="left">
                Authors
              </Box>
            </AccordionButton>
            <AccordionPanel pb={4} isOpen={accordionState.authors}>
                <Text> {authors}</Text>
            </AccordionPanel>
          </AccordionItem>
          <AccordionItem width="200">
            <AccordionButton onClick={() => handleAccordionClick("keyConcepts")} _expanded={{ bg: 'tomato', color: 'white' }}>
              <Box flex="1" textAlign="left">
                Key Concepts
              </Box>
            </AccordionButton>
            <AccordionPanel pb={4} isOpen={accordionState.keyConcepts}>
                <Text> {keyConcepts}</Text>
            </AccordionPanel>
          </AccordionItem>
          <AccordionItem>
            <AccordionButton onClick={() => handleAccordionClick("highlights")} _expanded={{ bg: 'tomato', color: 'white' }}>
              <Box flex="1" textAlign="left">
                Highlights
              </Box>
            </AccordionButton>
            <AccordionPanel pb={4} isOpen={accordionState.highlights}>
                <Text> {highlights}</Text>
            </AccordionPanel>
          </AccordionItem>
          <AccordionItem>
            <AccordionButton onClick={() => handleAccordionClick("summary")} _expanded={{ bg: 'tomato', color: 'white' }}>
              <Box flex="1" textAlign="left">
                Summary
              </Box>
            </AccordionButton>
            <AccordionPanel pb={4} isOpen={accordionState.summary}>
                <Text> {summary}</Text>
            </AccordionPanel>
          </AccordionItem>
          <AccordionItem>
            <AccordionButton onClick={() => handleAccordionClick("limitations")} _expanded={{ bg: 'tomato', color: 'white' }}>
              <Box flex="1" textAlign="left">
                Limitations
              </Box>
            </AccordionButton>
            <AccordionPanel pb={4} isOpen={accordionState.limitations}>
                <Text> {limitations}</Text>
            </AccordionPanel>
          </AccordionItem>
        </Accordion>

        </Box>
        <Box w="100%" maxW="xl" borderWidth="1px" borderRadius="lg" p="6"
          flex="1" 
          border="2px dashed gray"
          borderColor="gray.200"
          minHeight="100vh"
          >
          {/* <Text> Summary of the paper </Text> */}
          <Center>
            <Heading size="md">Extracted Resources</Heading>
          </Center>
          <VStack spacing={5}>
            <Menu>
              <MenuButton 
                as={Button} 
                onClick={() => toggleDropdown(0)}
                px={4}
                py={2}
                transition='all 0.2s'
                borderRadius='md'
                borderWidth='1px'
                _hover={{ bg: 'gray.400' }}
                _expanded={{ bg: 'blue.400' }}
                _focus={{ boxShadow: 'outline' }}>
                Tables
              </MenuButton>
              
              <MenuList display={dropdowns[0] ? "block" : "none"}>
                { loadingSummary && (
                    tables.map(table => (
                      <MenuItem>
                        <Box
                        w="200px"
                        h="200px"
                        boxSizing="border-box"
                        transition="transform 0.01s"
                        _hover={{ transform: "scale(3)" }}>
                          <Image src={`http://localhost:4949/images/${table}`} transformOrigin="center"  w="100%" h="100%" objectFit="scale-down" alt={table} />
                        </Box>
                      </MenuItem>
                      ))
                    )
                  }
              </MenuList>
            </Menu>
            <Menu direction='horizontal'>
              <MenuButton as={Button} onClick={() => toggleDropdown(1)}>
                Figures
              </MenuButton>
              <MenuList display={dropdowns[1] ? "block" : "none"}>
                <SimpleGrid minChildWidth='120px' >
                { loadingSummary && (
                  
                  figures.map(fig => (
                    <MenuItem>
                      <Box
                        w="200px"
                        h="200px"
                        p="4"
                        boxSizing="border-box"
                        transition="transform 0.01s"
                        _hover={{ transform: "scale(3 )" }}>
                        <Image src={`http://localhost:4949/images/${fig}`} transformOrigin="center" w="100%" h="100%" objectFit="scale-down" alt={fig} />
                      </Box>
                    </MenuItem>
                  ))
                  )
                }
                </SimpleGrid>
              </MenuList>
            </Menu>
          </VStack>
        </Box>
    
    <Box 
      width="300px"
      position="absolute"
      left="30"
      top="150"
    >
      <Box
        {...getRootProps()}
        border="2px dashed gray"
        borderRadius="md"
        p="4"
        transform="translateY(-50%)"
        borderWidth="2px"
        borderStyle="dashed"
        rounded="md"
        textAlign="center"
        borderColor={isDragActive ? 'green.400' : 'gray.200'}
        _hover={{
          borderColor: 'gray.300',
        }}
        cursor="pointer"
      >
        <input {...getInputProps()} />
        <Box as={FaFileUpload} color="gray.500" mb="2" />
        <Text fontSize="md" color="gray.500" fontWeight="medium">
          {isDragActive ? 'Drop files here' : 'Drag and drop files here or click to upload'}
        </Text>
        {isUploading && (
          <Box mt="4">
            <Spinner size="xl" />
            <Box mt="4" fontWeight="semibold" fontSize="lg">
              Uploading file...
            </Box>
          </Box>
        )}
        {isSuccess && (
          <Box mt="4">
            <Alert status="success">
              <AlertIcon />
              <AlertTitle>File uploaded successfully!</AlertTitle>
            </Alert>
          </Box>
        )}
      </Box>
      <VStack 
        pb={4} 
        spacing={4} 
        border="2px dashed gray"
        borderRadius="md"
        borderWidth="2px"
        borderStyle="dashed"
        rounded="md"
        textAlign="center"
        borderColor={'gray.200'}
      >
      {uploadedFileTitles.length > 0 ? (
        uploadedFileTitles.map((title, index) => (
        <Box
          key={index}
          bg={selectedFileTitle === title ? 'gray.200' : 'white'}
          p="2"
          m="2"
          borderRadius="md"
          cursor="pointer"
          borderWidth="1px"
          borderColor="gray.200"
          _hover={{
            bg: 'gray.100',
          }}
          onClick={() => handleItemClick(index)}
        >
          <Text fontSize='md'>{title}</Text>
        </Box>
          // {/* <Box key={index}> */}
            // {/* <Text>{file}</Text> */}
          // {/* </Box> */}
        ))
      ) : (
        <Text fontSize="md" color="gray.500" fontWeight="medium">None file is uploaded yet</Text>
      )}
      </VStack>
    </Box>
    </Flex>
  );
}
export default DragAndDrop;