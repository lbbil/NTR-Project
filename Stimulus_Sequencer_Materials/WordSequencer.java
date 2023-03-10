package fMRIWordSequencer;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;

/* Given a list of numbers, this program generates sequences of lists such that numbers that were previously neighbors
 * are not next to each other in successive lists. Neighbors are defined as numbers that are 4 indices to the left or
 * right of a index. */

/* IMPORTANT: The program will generate lists until it can and throw a IllegalArgumentException if all the lists
 * requested were not able to be generated. In this situation, you will have to run the program again until you are
 * able to get the lists. Also, depending on the size of the list and number of lists requested, it may be impossible
 * to generate the requested number of lists. */
public class WordSequencer {

	/* Determines the size of the list (as number gets smaller,it becomes harder to generate more lists) */
	public static int size = 40;
	
	/* Currently, the main method generates four lists. Can be copied to create new lists (but takes longer to run) */
	public static void main(String[] args) {		
		
		List<Integer> list1 = createList1(); 					// creates list of size elements in sequential order
		System.out.println(list1);
	
		Map<Integer, Set<Integer>> neighbors = new HashMap<>(); // creates initial HashMap to store neighbors
		
		for (Integer curr: list1) {
			neighbors.put(curr, new HashSet<Integer>()); 		// initializes each element (key value of HashMap)
		}
		
		updateNeighbors(list1, neighbors); 						// updates each element's neighbors from list1
				
		List<Integer> list2 = createLists(list1, neighbors); 	// creates list2
		/* System.out.println(checkFunction(list2, neighbors)); */
		updateNeighbors(list2, neighbors); 						// updates each element's neighbors from list2
		
		List<Integer> list3 = createLists(list1, neighbors); 	// creates list3
		/* System.out.println(checkFunction(list3, neighbors)); */
		updateNeighbors(list3, neighbors); 						// updates each element's neighbors from list3
		
		List<Integer> list4 = createLists(list1, neighbors); 	// creates list4
		/* System.out.println(checkFunction(list4, neighbors)); */
		
	}
	
	/* createList1: returns a list from 1 to size */
	private static List<Integer> createList1() {
		List<Integer> firstList = new ArrayList<>();
		for (int i = 1; i <= size; i++) {
			firstList.add(i);
		}
		return firstList;
 	}
	
	/* createLists: returns a list of elements where neighbors are not next to each other
	 * 
	 * parameters
	 * - list1: list of elements to create a list from
	 * - neighbors: map of neighbors for each element
	 *  */
	private static List<Integer> createLists(List<Integer> list1, Map<Integer, Set<Integer>> neighbors) {
		
		List<Integer> list2 = new ArrayList<>(); 			// stores new list
		List<Integer> toInclude = new ArrayList<>(list1); 	// elements that need to be put in list2
		
		Random random = new Random(); 						// used to generate random numbers
		int i = size; 										// starts at size because there are size elements
		
		int firstNumIndex = random.nextInt(i); 				// randomly selects index from 0 to size-1 (inclusive)
		Integer firstNum = toInclude.get(firstNumIndex); 	// element at randomly selected index
		
		list2.add(firstNum);								// firstNum is added to new list
		toInclude.remove(firstNumIndex);					// firstNum removed from toInclude so it is not added again
		i--;		 										// decrements i because element was removed from toInclude
		
		List<Integer> discarded = new ArrayList<>(toInclude); // elements from toInclude that have not been "tried" yet
		
		int secondNumIndex = random.nextInt(i);		 		// randomly selects index from 0 to size-2 (inclusive)
		Integer secondNum = toInclude.get(secondNumIndex); 	// element at randomly selected index
		
		int discardedIndex = i; 							// index starts at number of elements in toInclude
		
		// while an secondNum is a neighbor of the firstNum of list 2 and there are still alternate numbers
		while ((!discarded.isEmpty()) && neighbors.get(firstNum).contains(secondNum)) {
			discarded.remove(secondNumIndex); 				// secondNum is a neighbor so it is removed from discarded
			discardedIndex--; 								// discardedIndex is decremented because list gets smaller
			
			secondNumIndex = random.nextInt(discardedIndex); // new number is selected
			secondNum = discarded.get(secondNumIndex);			
		}
		
		secondNumIndex = toInclude.indexOf(secondNum);		// new secondNumIndex
		
		if (!discarded.isEmpty()) { 						// second number is found
			list2.add(secondNum);
			toInclude.remove(secondNumIndex);
			i--;
			discarded = new ArrayList<>(toInclude); 		// resets discarded list
		} else {
			return null;
		}
		
		int thirdNumIndex = random.nextInt(i); 				// randomly selects index from 0 to size-3 (inclusive)
		Integer thirdNum = toInclude.get(thirdNumIndex);
		
		discardedIndex = i;
		
		// while an thirdNum is a neighbor of the firstNum and secondNum of list 2 and there are still alternate numbers
		while ((neighbors.get(firstNum).contains(thirdNum) || neighbors.get(secondNum).contains(thirdNum)) 
				&& (!discarded.isEmpty())) {
			discarded.remove(thirdNumIndex); 				// thirdNum is a neighbor so it is removed from discarded
			discardedIndex--; 								// discardedIndex is decremented because list gets smaller
			thirdNumIndex = random.nextInt(discardedIndex); // new number is selected
			thirdNum = discarded.get(thirdNumIndex);
		}
		
		thirdNumIndex = toInclude.indexOf(thirdNum); 		// new thirdNumIndex
		
		if (!discarded.isEmpty()) { 						// third number is found
			list2.add(thirdNum);
			toInclude.remove(thirdNumIndex);
			i--;
			discarded = new ArrayList<>(toInclude); 		// resets discarded list
		} else {
			return null;
		}
		
		int fourthNumIndex = random.nextInt(i); 			// randomly selects index from 0 to size-4 (inclusive)
		Integer fourthNum = toInclude.get(fourthNumIndex);
		
		discardedIndex = i;
		
		// while element is a neighbor of the firstNum, secondNum, thirdNum of list 2 and there are still other numbers
		while ((neighbors.get(firstNum).contains(fourthNum) 
				|| neighbors.get(secondNum).contains(fourthNum) 
				|| neighbors.get(thirdNum).contains(fourthNum)) && (!discarded.isEmpty())) {
			discarded.remove(fourthNumIndex);
			discardedIndex--;
			fourthNumIndex = random.nextInt(discardedIndex);
			fourthNum = discarded.get(fourthNumIndex);
		}
		
		fourthNumIndex = toInclude.indexOf(fourthNum);

		if (!discarded.isEmpty()) { 						// fourth num found
			list2.add(fourthNum);
			toInclude.remove(fourthNumIndex);
			i--;
			discarded = new ArrayList<>(toInclude);
		} else {
			return null;
		}
		
		/* */
		for (int x = 5; x <= size; x++) {
			int nthNumIndex = random.nextInt(i);
			Integer nthNum = toInclude.get(nthNumIndex);
			
			discardedIndex = i;
			
			// variables store the word 4 to the left, 3 to the left, 2 to the left, and 1 to the left of the element
			Integer fourToLeft = list2.get(x - 5);
			Integer threeToLeft = list2.get(x - 4);
			Integer twoToLeft = list2.get(x - 3);
			Integer oneToLeft = list2.get(x - 2);
			
			// checks if selected element is contained in neighbors list of the variables above
			while ((neighbors.get(fourToLeft).contains(nthNum) 
					|| neighbors.get(threeToLeft).contains(nthNum) 
					|| neighbors.get(twoToLeft).contains(nthNum) 
					|| neighbors.get(oneToLeft).contains(nthNum)) && (!discarded.isEmpty())) {
				discarded.remove(nthNumIndex);
				discardedIndex--;
				nthNumIndex = random.nextInt(discardedIndex);
				nthNum = discarded.get(nthNumIndex); 		// new number is selected if it is a neighbor
				
			}
			
			nthNumIndex = toInclude.indexOf(nthNum);
			
			if (!discarded.isEmpty()) { 					//nth num found
				list2.add(nthNum);
				toInclude.remove(nthNumIndex);
				i--;
				discarded = new ArrayList<>(toInclude);
			} else {
				return null;
			}
		}
			
		System.out.println(list2);
		return list2;
		
	}
	
	/* updateNeighbors: records neighbors of each element in a HashMap
	 * 
	 * parameters
	 * - list: list of elements to check neighbors of
	 * - neighbors: map that contains all the neighbors for each element (is updated after each list is created)
	 *  */
	private static void updateNeighbors(List<Integer> list, Map<Integer, Set<Integer>> neighbors) {
		for (Integer curr: list) {
			int elementIndex = list.indexOf(curr);
															// adds the 4 neighbors to the right of the current element
			for (int i = 1; i <= 4; i++) {
				int neighborIndex = elementIndex + i;
				if (neighborIndex < list.size()) {
					neighbors.get(curr).add(list.get(neighborIndex));
				}
			}
															// adds the 4 neighbors to the left of the current element
			for (int i = 1; i <= 4; i++) {
				int neighborIndex = elementIndex - i;
				if (neighborIndex >= 0) {
					neighbors.get(curr).add(list.get(neighborIndex));
				}
			}
		}
		/* System.out.println(neighbors); */ 				// uncomment this to see neighbors list
	}
	
	/* checkFunction: checks if list elements are next to neighbors
	 * 
	 * parameters
	 * - list: list of elements to check neighbors of
	 * - neighbors: map that contains all the neighbors for each element (is updated after each list is created)
	 *  */
	private static boolean checkFunction(List<Integer> list, Map<Integer, Set<Integer>> neighbors) {
		for (int i = 0; i < size - 4; i++) {
			Integer curr = list.get(i);
			Integer neighborOne = list.get(i + 1);
			Integer neighborTwo = list.get(i + 2);
			Integer neighborThree = list.get(i + 3);
			Integer neighborFour = list.get(i + 4);
			
			if (neighbors.get(neighborOne).contains(curr) || neighbors.get(neighborTwo).contains(curr)
					|| neighbors.get(neighborThree).contains(curr) || neighbors.get(neighborFour).contains(curr)) {
				return false;
			}
		}

		Integer neighborOne = list.get(size - 3);
		Integer neighborTwo = list.get(size - 2);
		Integer neighborThree = list.get(size - 1);
		if (neighbors.get(neighborOne).contains(list.get(size - 4)) 
				|| neighbors.get(neighborTwo).contains(list.get(size - 4))
				|| neighbors.get(neighborThree).contains(list.get(size - 4))) {
			return false;
		}

		neighborOne = list.get(size - 2);
		neighborTwo = list.get(size - 1);
		if (neighbors.get(neighborOne).contains(list.get(size - 3)) 
				|| neighbors.get(neighborTwo).contains(list.get(size - 3))) {
			return false;
		}

		neighborOne = list.get(size - 1);
		if (neighbors.get(neighborOne).contains(list.get(size - 2))) {
			return false;
		}
		return true;
		
	}

}
