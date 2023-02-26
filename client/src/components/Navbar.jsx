import { useState } from 'react';
import {
  Box,
  Flex,
  Text,
  Button,
  IconButton,
  useDisclosure,
  useColorModeValue,
  useBreakpointValue,
  HStack,
  VStack,
} from '@chakra-ui/react';
import { HamburgerIcon, CloseIcon } from '@chakra-ui/icons';

const Navbar = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [active, setActive] = useState('Home');

  const buttonColor = useColorModeValue('gray.800', 'white');

  const navItems = ['Home', 'Presentations', 'About Us'];
  const authItems = ['Login', 'Sign up'];

  const isActive = (item) => active === item;

  const handleItemClick = (item) => {
    setActive(item);
    onClose();
  };
  const navSpacing = useBreakpointValue({ base: 4, md: 8 });
  const authSpacing = useBreakpointValue({ base: 4, md: 8 });

  return (
    <Box bg={useColorModeValue('gray.100', 'gray.900')} px={4}>
      <Flex h={16} alignItems={'center'} justifyContent={'space-between'}>
        <IconButton
          size={'md'}
          icon={isOpen ? <CloseIcon /> : <HamburgerIcon />}
          aria-label={'Open Menu'}
          display={{ md: !isOpen ? 'none' : 'inherit' }}
          onClick={isOpen ? onClose : onOpen}
        />
        <HStack maxW="xlg" align="start" alignItems={'center'}>
          <Text fontWeight="bold" fontSize="2xl">
            Summed
          </Text>
          <Text fontSize="md" color={useColorModeValue('gray.600', 'gray.400')}>
            An AI-powered tool to ease your pain with medical literature
          </Text>
        </HStack>
        <Flex alignItems={'center'}>
          <HStack as={'nav'} spacing={4} display={{ base: 'none', md: 'flex' }}>
            {navItems.map((item) => (
              <Button
                key={item}
                variant="ghost"
                onClick={() => handleItemClick(item)}
                color={isActive(item) ? 'teal.500' : buttonColor}
              >
                {item}
              </Button>
            ))}
          </HStack>
          <HStack as={'nav'} spacing={4} display={{ base: 'none', md: 'flex' }}>
            {authItems.map((item) => (
              <Button
                key={item}
                colorScheme="teal"
                variant="solid"
                onClick={() => handleItemClick(item)}
                color={isActive(item) ? 'white' : buttonColor}
              >
                {item}
              </Button>
            ))}
          </HStack>
        </Flex>
      </Flex>

      {isOpen ? (
        <Box pb={4} display={{ md: 'none' }}>
          <HStack as={'nav'} spacing={4}>
            {navItems.map((item) => (
              <Button
                key={item}
                variant="ghost"
                onClick={() => handleItemClick(item)}
                color={isActive(item) ? 'teal.500' : buttonColor}
              >
                {item}
              </Button>
            ))}
            {authItems.map((item) => (
              <Button
                key={item}
                colorScheme="teal"
                variant="solid"
                onClick={() => handleItemClick(item)}
                color={isActive(item) ? 'white' : buttonColor}
              >
                {item}
              </Button>
            ))}
          </HStack>
        </Box>
      ) : null}
    </Box>
  );
};

export default Navbar;
