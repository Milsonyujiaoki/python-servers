package main

import (
	"fmt"
	"log"
	"net/http"
)

func main (){
	http.HandleFunc("/",func(w http.ResponseWriter, r *http.Request){
		fmt.Fprintln(w, "<h1>Server Go</h1>")
	})
	log.Fatal(http.ListenAndServe("0.0.0.0:8104", nil))
}
