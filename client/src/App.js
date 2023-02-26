import Chatbot from './components/Chatbot';
import DragAndDrop from './components/DragDrop';
import Navbar from './components/Navbar';
import Canvas from './components/Canvas';
import { ChakraProvider, Container, Heading, Text } from '@chakra-ui/react';

const App = () => (
  <ChakraProvider>
    <Navbar />
    <Container maxW="container.lg" centerContent>
      {/* <Heading as="h1" size="2xl" my="8"> */}
        {/* Summed */}
      {/* </Heading> */}
      {/* <Text fontSize="lg" mb="8" fontWeight="bold"> */}
        {/* An AI-powered tool to summarize your medical documents */}
      {/* </Text> */}
      <div>
        <DragAndDrop />            
        <Chatbot />
      </div>
    </Container>
  </ChakraProvider>
);

export default App;
