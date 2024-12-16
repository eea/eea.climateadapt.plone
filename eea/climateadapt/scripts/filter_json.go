package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
)

type Object struct {
	Type string `json:"@type"`
}

func main() {
	// Define command-line arguments
	inputFilePath := flag.String("input", "", "Path to the input JSON file")
	outputFilePath := flag.String("output", "output.json", "Path to the output JSON file")
	filterType := flag.String("type", "", "Filter type for @type property (e.g., Folder)")

	flag.Parse()

	// Validate input
	if *inputFilePath == "" || *filterType == "" {
		fmt.Println("Error: Input file path and type filter must be provided.")
		flag.Usage()
		os.Exit(1)
	}

	// Read the input file
	inputData, err := os.ReadFile(*inputFilePath)
	if err != nil {
		fmt.Printf("Error reading input file: %v\n", err)
		os.Exit(1)
	}

	// Parse JSON data
	var objects []map[string]interface{}
	if err := json.Unmarshal(inputData, &objects); err != nil {
		fmt.Printf("Error parsing JSON: %v\n", err)
		os.Exit(1)
	}

	// Filter objects
	var filteredObjects []map[string]interface{}
	for _, obj := range objects {
		if obj["@type"] == *filterType {
			filteredObjects = append(filteredObjects, obj)
		}
	}

	// Write to output file
	outputData, err := json.MarshalIndent(filteredObjects, "", "  ")
	if err != nil {
		fmt.Printf("Error generating output JSON: %v\n", err)
		os.Exit(1)
	}

	if err := os.WriteFile(*outputFilePath, outputData, 0644); err != nil {
		fmt.Printf("Error writing output file: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Filtered JSON written to %s\n", *outputFilePath)
}
